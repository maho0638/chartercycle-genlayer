// Pure read-only follow-up on Studio returned transaction ID and fee policy.
const RPC='https://studio.genlayer.com/api';
const ids={attempt:'0xa3a54786ad8be7d19417c2aec23fd4295ba8a3775cb396b22b866574b1718162',previous:'0x1bb7bd94870c7c9beb7b1ae805ab9d158809d9698cecc0927a86c7af759fa5a8',success:'0x64fecea121383944bfdb8bef4a28be741c97d47fc4fec7c2de1e3829d7487b3e'};
async function rpc(method,params=[]){const r=await fetch(RPC,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',method,params,id:7}),signal:AbortSignal.timeout(18000)});return await r.json()}
for (const [name,id] of Object.entries(ids)){
 for (const method of ['eth_getTransactionByHash','eth_getTransactionReceipt','gen_getTransactionStatus']){
  const v=await rpc(method,[id]);if(v.error){console.log('STATE_'+name+'_'+method+'_ERROR='+JSON.stringify(v.error).slice(0,320));continue}
  const data=v.result;const output=typeof data==='object'&&data!==null?Object.fromEntries(['status','hash','transactionHash','gas','gasUsed','from','to','nonce','value','gaslimit','blockNumber','error','result','created_at','consensus_data','consensus_history','input_data'].filter(k=>k in data).map(k=>[k, ['consensus_data','consensus_history','input_data'].includes(k)?JSON.stringify(data[k]).slice(0,800):data[k]])):data;
  console.log('STATE_'+name+'_'+method+'='+JSON.stringify(output).slice(0,1800));
 }
}
const f=await rpc('sim_getFeeConfig');
if(f.error)console.log('STUDIO_FEES_ERROR='+JSON.stringify(f.error).slice(0,800));
else{
 const v=f.result;
 console.log('STUDIO_FEES_ENABLED='+String(v.enabled));
 console.log('STUDIO_DEFAULT_FEES='+JSON.stringify(v.defaultFees||null).slice(0,9000));
 console.log('STUDIO_FEE_POLICY='+JSON.stringify(v.policy||null).slice(0,1400));
}
