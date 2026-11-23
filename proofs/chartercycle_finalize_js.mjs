/** Single guarded Studionet finalize through official GenLayerJS SDK v1.1.8.
 *  No deployment, no private-key output, no extra proposals or other writes.
 */
import { createClient, createAccount } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';

const CONTRACT='0x5506E19b990cD9839659855AEC2fcA7c761867e8';
const PROPOSAL='live_timelock_lifecycle_v1';
const CLOSES=1795462930;
const READY=1795549330;
const client=createClient({chain:studionet,account:createAccount()});
if (studionet.id!==61999 || studionet.isStudio!==true) throw Error('Unexpected network config');
const sleep=(ms)=>new Promise(r=>setTimeout(r,ms));
const rpc=async(method,params=[])=>{
  const res=await fetch('https://studio.genlayer.com/api',{
    method:'POST',headers:{'content-type':'application/json'},
    body:JSON.stringify({jsonrpc:'2.0',method,params,id:1}),
    signal:AbortSignal.timeout(20000)
  });
  if(!res.ok) throw Error(method+' HTTP '+res.status);
  const data=await res.json();
  if(data.error) throw Error(method+' '+JSON.stringify(data.error).slice(0,300));
  return data.result;
};
const read=async(fn,args=[])=>{
  let value=await client.readContract({address:CONTRACT,functionName:fn,args});
  if(typeof value==='string') return JSON.parse(value);
  if(value && typeof value==='object') return value;
  throw Error('Unexpected GenLayer view response '+typeof value);
};
const proposal=await read('get_proposal',[PROPOSAL]);
const charter=await read('get_charter');
console.log('JS_NETWORK='+studionet.id+' STUDIO='+studionet.isStudio);
console.log('JS_STATUS_BEFORE='+proposal.status+' YES='+proposal.yes+' NO='+proposal.no+' VERSION='+charter.version);
if(proposal.id!==PROPOSAL||Number(proposal.yes)!==2||Number(proposal.no)!==0||Number(proposal.closes)!==CLOSES||Number(charter.version)!==1) throw Error('State preconditions changed; no send');
if(proposal.status==='TIMELOCK'||proposal.status==='ENACTED'){console.log('JS_ALREADY_FINALIZED_NO_SEND');process.exit(0)}
if(proposal.status!=='VOTING') throw Error('Not in VOTING state');
const block=await rpc('eth_getBlockByNumber',['latest',false]);
const timestamp=parseInt(block.timestamp,16);
if(timestamp<CLOSES) throw Error('Voting still open; no send');
console.log('JS_BLOCK_TIMESTAMP='+timestamp);
let attempted=false;
try{
  attempted=true;
  const txId=await client.writeContract({
    address:CONTRACT,functionName:'finalize',args:[PROPOSAL],value:0n
  });
  if(typeof txId!=='string'||!/^0x[0-9a-fA-F]{64}$/.test(txId)) throw Error('Invalid tx id '+String(txId));
  console.log('JS_FINALIZE_TX='+txId);
  let status='';
  let state='';
  for(let i=0;i<85;i++){
    try{status=String(await rpc('gen_getTransactionStatus',[txId]));}
    catch(e){if(i>25)console.log('JS_POLL='+String(e).slice(0,180))}
    try{state=(await read('get_proposal',[PROPOSAL])).status;}
    catch(e){if(i>25)console.log('JS_READ='+String(e).slice(0,180))}
    if((status==='FINALIZED'||status==='ACCEPTED')&&state==='TIMELOCK')break;
    if(['CANCELED','UNDETERMINED','LEADER_TIMEOUT','VALIDATORS_TIMEOUT'].includes(status))break;
    await sleep(2000);
  }
  console.log('JS_TX_STATUS='+status+' PROPOSAL_STATUS='+state);
  if(state!=='TIMELOCK')throw Error('No TIMELOCK state; do not infer success, tx '+txId);
  const after=await read('get_proposal',[PROPOSAL]);
  if(Number(after.ready_at)!==READY) throw Error('Wrong timelock ready_at');
  console.log('JS_FINALIZE_SUCCESS='+txId);
  console.log('JS_READY_AT='+after.ready_at);
}catch(error){
  console.log('JS_ONE_SHOT_ERROR='+String(error).slice(0,1000));
  if(attempted)console.log('JS_NO_AUTOMATIC_RETRY');
  process.exitCode=1;
}
