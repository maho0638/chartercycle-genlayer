import { createClient, createAccount } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';

const CONTRACT="0x5506E19b990cD9839659855AEC2fcA7c761867e8";
const ID="live_timelock_lifecycle_v1";
const CLOSES=1795462930;
const READY=1795549330;
const account=createAccount();
const client=createClient({chain:studionet,account});
const get=async (fn,args=[])=>{
 const d=await client.readContract({address:CONTRACT,functionName:fn,args});
 return typeof d==="string"?JSON.parse(d):d;
};
const rpc=async(method,params=[])=>{
 const r=await fetch('https://studio.genlayer.com/api',{
  method:'POST',headers:{'content-type':'application/json'},
  body:JSON.stringify({jsonrpc:"2.0",method,params,id:1}),
  signal:AbortSignal.timeout(15000)
 });
 if(!r.ok)throw Error(method+" HTTP "+r.status);
 const j=await r.json();if(j.error)throw Error(method+" "+JSON.stringify(j.error).slice(0,200));
 return j.result;
};
if(studionet.id!==61999||studionet.isStudio!==true)throw Error("Not expected Studionet 61999");
const p=await get('get_proposal',[ID]);const charter=await get('get_charter');
console.log("MAINSDK_STATUS="+p.status+" YES="+p.yes+" NO="+p.no+" VERSION="+charter.version);
if(p.id!==ID||Number(p.yes)!==2||Number(p.no)!==0||Number(p.closes)!==CLOSES||Number(charter.version)!==1)throw Error("State changed, abort");
if(p.status==="TIMELOCK"||p.status==="ENACTED"){console.log("MAINSDK_NO_SEND_ALREADY_DONE");process.exit(0)}
if(p.status!=="VOTING")throw Error("Unexpected stage; abort");
const block=await rpc("eth_getBlockByNumber",["latest",false]);if(parseInt(block.timestamp,16)<CLOSES)throw Error("Voting not yet closed");
let feeOpts=undefined;
try {
 const quote=await client.estimateTransactionFeesForWrite({
  address:CONTRACT,functionName:'finalize',args:[ID],account,
  leaderTimeunitsAllocation:125n,
  validatorTimeunitsAllocation:250n,
  executionBudgetPerRound:786500n,
  appealRounds:1n,
  rotations:[0n,0n],
 });
 const fee=BigInt(quote.feeValue);
 console.log("MAINSDK_ESTIMATED_PROTOCOL_FEE="+fee.toString());
 // Studio supports fee budgeting; quote derived using native simulator, not an invented amount.
 feeOpts={distribution:quote.distribution,feeValue:quote.feeValue};
} catch(e) {
 console.log("MAINSDK_FEE_ESTIMATE_UNAVAILABLE="+String(e).slice(0,380));
 // Do NOT spend or submit if fee requirements cannot be independently assessed.
 const cfg=await rpc('sim_getFeeConfig',[]).catch(()=>null);
 console.log("MAINSDK_STUDIO_FEE_CONFIG="+JSON.stringify(cfg)?.slice(0,800));
 if(cfg&&JSON.stringify(cfg).includes('"enabled":true'))throw Error("Fee config enabled but estimation failed; abort");
}
let txId;
try{
 txId=await client.writeContract({
  address:CONTRACT,functionName:'finalize',args:[ID],account,
  value:0n,...(feeOpts?{fees:feeOpts}:{})
 });
 console.log("MAINSDK_FINALIZE_TX_ID="+txId);
}catch(e){
 console.log("MAINSDK_SUBMISSION_ERROR="+String(e).slice(0,1100));
 process.exitCode=1;
}
if(txId){
 let status='',stage='';
 for(let i=0;i<80;i++){
  status=String(await rpc("gen_getTransactionStatus",[txId]).catch(()=>"..."));
  stage=String((await get('get_proposal',[ID]).catch(()=>({status:"..."}))).status);
  if(stage==='TIMELOCK'&&(status==='FINALIZED'||status==='ACCEPTED'))break;
  if(['CANCELED','UNDETERMINED'].includes(status))break;
  await new Promise(r=>setTimeout(r,1800));
 }
 console.log("MAINSDK_CONSENSUS_STATUS="+status+" STAGE="+stage);
 if(stage!=='TIMELOCK') throw Error("No finalized TIMELOCK proof for "+txId);
 const after=await get('get_proposal',[ID]);
 if(Number(after.ready_at)!==READY) throw Error("Timelock ready_at mismatch");
 console.log("MAINSDK_FINALIZE_SUCCESS="+txId);
}
