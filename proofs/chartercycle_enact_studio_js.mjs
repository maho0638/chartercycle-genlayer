/**
 * CharterCycle — once-only, fee-aware live Studionet enactment verification.
 *
 * The 24h vote and 24h timelock are immutable contract rules. This uses the
 * already deployed contract and already FINALIZED proposal; no new deployment
 * or governance proposal. Every branch is fail-closed. Never print wallet keys.
 *
 * Execution before ready_at is READ-ONLY. An ENACTED state never sends again.
 */
import {createClient, createAccount} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';

const CONTRACT = '0x5506E19b990cD9839659855AEC2fcA7c761867e8';
const PROPOSAL = 'live_timelock_lifecycle_v1';
const CLOSES = 1795462930;
const READY = 1795549330;
const RPC = 'https://studio.genlayer.com/api';
const MAX_FEE = 1000000000000000000n;
const account = createAccount();
const client = createClient({chain: studionet, account});
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function rpc(method, params = []) {
  const response = await fetch(RPC, {
    method: 'POST',
    headers: {'content-type': 'application/json'},
    body: JSON.stringify({jsonrpc: '2.0', method, params, id: 1}),
    signal: AbortSignal.timeout(20000),
  });
  if (!response.ok) throw Error(`${method} HTTP ${response.status}`);
  const doc = await response.json();
  if (doc.error) throw Error(`${method}: ${JSON.stringify(doc.error).slice(0,350)}`);
  return doc.result;
}

async function read(name, args = []) {
  const value = await client.readContract({
    address: CONTRACT,
    functionName: name,
    args,
  });
  const decoded = typeof value === 'string' ? JSON.parse(value) : value;
  if (!decoded || typeof decoded !== 'object') throw Error(`Invalid ${name} output`);
  return decoded;
}

function assertOriginalProof(proposal) {
  if (proposal.id !== PROPOSAL ||
      proposal.base_version !== 1 ||
      Number(proposal.closes) !== CLOSES ||
      Number(proposal.yes) !== 2 ||
      Number(proposal.no) !== 0 ||
      !/^[a-f0-9]{64}$/i.test(String(proposal.candidate_hash))) {
    throw Error('Governance proof differs from the independently verified 2-of-3 vote; abort');
  }
}

async function verifyEnacted() {
  const [p, charter] = await Promise.all([
    read('get_proposal', [PROPOSAL]),
    read('get_charter'),
  ]);
  assertOriginalProof(p);
  if (p.status !== 'ENACTED' ||
      Number(charter.version) !== 2 ||
      charter.sha256 !== p.candidate_hash ||
      !Number.isSafeInteger(Number(p.executed_at)) ||
      Number(p.executed_at) < READY) {
    throw Error('ENACTED status, charter version/hash or executed_at proof mismatch');
  }
  console.log('ENACT_PROVEN=ENACTED_VERSION_2');
  console.log('ENACT_CONTRACT=' + CONTRACT);
  console.log('ENACT_PROVEN_SHA256=' + charter.sha256);
  console.log('ENACT_EXECUTED_AT=' + p.executed_at);
}

if (studionet.id !== 61999 || studionet.isStudio !== true) {
  throw Error('Not pinned GenLayer Studionet chain 61999');
}
const chain = await rpc('eth_chainId', []);
if (Number(BigInt(chain)) !== 61999) throw Error('RPC chain mismatch');

const [proposal, charter, block] = await Promise.all([
  read('get_proposal', [PROPOSAL]),
  read('get_charter'),
  rpc('eth_getBlockByNumber', ['latest', false]),
]);
assertOriginalProof(proposal);
console.log('ENACT_CHAIN=61999');
console.log('ENACT_BEFORE=' + proposal.status);
console.log('ENACT_VERSION_BEFORE=' + charter.version);
const chainNow = Number(BigInt(block.timestamp));
console.log('ENACT_CHAIN_TIME=' + chainNow);
console.log('ENACT_READY_AT=' + READY);

if (proposal.status === 'ENACTED') {
  await verifyEnacted();
  console.log('ENACT_ALREADY_DONE_NO_NEW_TX');
  process.exit(0);
}
if (proposal.status !== 'TIMELOCK' ||
    Number(proposal.ready_at) !== READY ||
    Number(charter.version) !== 1) {
  throw Error('Not the authorized timelock state; abort before sending');
}
if (chainNow < READY) {
  console.log('ENACT_NOT_READY_READ_ONLY_NO_TX');
  console.log('ENACT_REMAINING_SECONDS=' + (READY - chainNow));
  process.exit(0);
}
// Verify live, server-supplied Studio fee envelope rather than the old Python
// SDK's EVM compatibility receipt or an undersized local estimator.
const feeConfig = await rpc('sim_getFeeConfig', []);
if (feeConfig?.enabled !== true ||
    !feeConfig.defaultFees?.distribution ||
    !feeConfig.policy) {
  throw Error('No trusted current Studionet fees; abort');
}
const fees = feeConfig.defaultFees;
const distribution = fees.distribution;
const fee = BigInt(fees.feeValue);
const executionBudget = BigInt(distribution.executionBudgetPerRound);
const budgetFloor = BigInt(feeConfig.policy.genvmStartBudgetFloor);
if (fee <= 0n || fee > MAX_FEE || executionBudget < budgetFloor) {
  throw Error('Studio fee quote failed safe bounds');
}
if (!Array.isArray(distribution.rotations) ||
    distribution.rotations.length !== Number(distribution.appealRounds) + 1) {
  throw Error('Fee rotations malformed');
}
for (const field of [
  'leaderTimeunitsAllocation',
  'validatorTimeunitsAllocation',
  'executionBudgetPerRound',
  'maxPriceGenPerTimeUnit',
  'storageFeeMaxGasPrice',
  'receiptFeeMaxGasPrice',
]) {
  if (BigInt(distribution[field]) <= 0n) throw Error('Fee field malformed: ' + field);
}
console.log('ENACT_MAX_PROTOCOL_FEE_WEI=' + fee.toString());
// At most one network write per workflow run. Do not retry on ambiguity.
const txId = await client.writeContract({
  address: CONTRACT,
  functionName: 'enact',
  args: [PROPOSAL],
  account,
  value: 0n,
  fees,
});
if (!/^0x[\da-fA-F]{64}$/.test(String(txId))) {
  throw Error('Enact submitted but returned invalid tx ID: ' + String(txId));
}
console.log('ENACT_SUBMITTED_TX=' + txId);
let lastStatus = '';
for (let i = 0; i < 115; ++i) {
  try {
    lastStatus = String(await rpc('gen_getTransactionStatus', [txId]));
  } catch (error) {
    if (i === 0 || i % 20 === 0) console.log('ENACT_POLL_ERROR=' + String(error).slice(0,160));
  }
  if (lastStatus === 'FINALIZED') break;
  if (['CANCELED', 'UNDETERMINED', 'LEADER_TIMEOUT', 'VALIDATORS_TIMEOUT'].includes(lastStatus)) {
    throw Error(`Enact consensus unsuccessful: ${lastStatus}; tx=${txId}`);
  }
  await sleep(2000);
}
console.log('ENACT_TX_STATUS=' + lastStatus);
if (lastStatus !== 'FINALIZED') {
  throw Error(`Enact still unfinalized; do not resubmit blindly. Tx=${txId} Status=${lastStatus}`);
}
await verifyEnacted();
console.log('ENACT_FINALIZED_TX=' + txId);
