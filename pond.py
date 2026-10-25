import json, pathlib, time, hashlib
from datetime import datetime, timezone
ROOT = pathlib.Path.home() / "pond"
CHAIN = ROOT / "chain.json"
LOCK = ROOT / "attic" / "pond.lock"
import sys
sys.path.insert(0, str(ROOT))
from kernel.consensus.pow import hash_header, mine, meets_target
from kernel.consensus.difficulty import get_difficulty
from kernel.consensus.merkle import merkle_root
from kernel.consensus.time_oracle import get_times

def load_chain():
 return json.loads(CHAIN.read_text())
def save_chain(chain):
 tmp = CHAIN.with_suffix(".tmp")
 tmp.write_text(json.dumps(chain))
 tmp.rename(CHAIN)
def get_module_hash(path):
 p = ROOT / path
 if not p.exists(): return "0"*8
 try: return hashlib.sha256(p.read_bytes()).hexdigest()[:12]
 except: return "0"*8

def mine_loop():
 while True:
  try:
   chain = load_chain()
   prev_block = chain[-1]
   prev_hash = prev_block["hash"]
   index = prev_block.get("index", len(chain)-1) + 1
   # 10MIN RULE v5.4
   last_ts = prev_block.get("payload",{}).get("ts")
   try:
    prev_t = datetime.fromisoformat(last_ts.replace("Z","+00:00")).timestamp() if last_ts else time.time()
   except: prev_t = time.time()
   elapsed = time.time() - prev_t
   MIN=600
   if elapsed < MIN:
    wait=MIN-elapsed
    print(f"10MIN RULE: {elapsed:.1f}s elapsed, sleeping {wait:.1f}s until next block... #{index}", flush=True)
    time.sleep(min(wait,60))
    continue
   difficulty = get_difficulty(index)
   wallet_pool_path = ROOT / "kernel" / "modules" / "wallet" / "tx_pool.json"
   try:
    pool = json.loads(wallet_pool_path.read_text()).get("pool", []) if wallet_pool_path.exists() else []
   except: pool=[]
   coinbase = {"type":"coinbase","to":"did:pond:biougra-a13","amount":50,"height":index}
   txs = [coinbase] + pool
   mr = merkle_root(txs)
   cables_h = get_module_hash("kernel/modules/cables/seabed_state.json")
   drones_h = get_module_hash("kernel/modules/drones/fleet_state.json")
   stamp_h = get_module_hash("kernel/modules/stamp/outbox/summary.json")
   times = get_times()
   ts_iso = datetime.now(timezone.utc).isoformat()
   btcHeight = times.get("btcHeight", 0)
   print(f"[{index}] Mining diff={difficulty} prev={prev_hash[:8]} mr={mr[:8]} btc={btcHeight} after {elapsed:.1f}s...", flush=True)
   nonce, block_hash = mine(prev_hash, mr, ts_iso, btcHeight, difficulty, index, cables_h, drones_h, stamp_h, index)
   if nonce is None:
    print(f"Failed to mine {index} in range, retry")
    time.sleep(1)
    continue
   payload = {
    "index": index,
    "ts": ts_iso,
    "btcHeight": btcHeight,
    "sunAltitude": prev_block.get("payload",{}).get("sunAltitude", 15.2),
    "cables_hash": cables_h,
    "drones_hash": drones_h,
    "stamp_hash": stamp_h,
    "wallet_height": index,
    "merkle_root": mr,
    "coinbase": coinbase,
    "block_time_target": 600
   }
   block = {
    "hash": block_hash,
    "prev": prev_hash,
    "index": index,
    "nonce": nonce,
    "difficulty": difficulty,
    "merkle_root": mr,
    "payload": payload
   }
   chain.append(block)
   save_chain(chain)
   print(f"✅ MINED #{index} hash={block_hash} nonce={nonce} diff={difficulty} drift={times.get('drift',0)}s", flush=True)
   time.sleep(1)
  except Exception as e:
   print(f"mine err {e}", flush=True)
   import traceback; traceback.print_exc()
   time.sleep(5)

if __name__ == "__main__":
 print(f"POND START v5.4 TARDIGRADE 10min blocks CAP3 LIVE MIN=600s", flush=True)
 mine_loop()
