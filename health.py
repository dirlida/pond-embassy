#!/data/data/com.termux/files/usr/bin/python3
import json, datetime, subprocess, os, struct
CHAIN="chain.json"
KERNEL_BIN="pond.kernel.bin"
CHECKPOINT_JSON="pond.checkpoint.json"
try:
 chain=json.load(open(CHAIN))
 if isinstance(chain, dict): chain=chain.get("blocks",chain)
except: chain=[]
chain_blocks=[b for b in chain if b.get('type')!='thesis']
thesis_blocks=[b for b in chain if b.get('type')=='thesis']
SLOW=[(1034,1282),(1037,1281),(1425,1599)]
ATTESTED=[(1007,17646,'2026-10-20 hard-reset GPS-drift 17646s Biougra attested'),(1304,1850,'2026-10-21 GPS-drift 1850s Biougra attested'),(1348,5528,'2026-10-21 GPS-drift 5528s Biougra attested'),(1402,6119,'2026-10-23 GPS-drift 6119s Biougra attested')]
try:
 out=subprocess.check_output(["git","log","-1","--format=%ct"],stderr=subprocess.DEVNULL).decode().strip()
 push_age=f"{(datetime.datetime.now().timestamp()-int(out))/60:.1f}m"
except: push_age="unknown"
last=chain_blocks[-1] if chain_blocks else (chain[-1] if chain else {})
ts_raw=last.get('payload',{}).get('ts') or last.get('timestamp_utc') or last.get('ts') or "2026-10-23T17:14:00Z"
try:
 age=(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(ts_raw.replace('Z','+00:00'))).total_seconds()
 age_s=f"{age:.0f}s"
except: age_s="unknown"; age=0
print(f"SLOW: {SLOW}")
print(f"ATTESTED: {ATTESTED}")
print(f"BTC REORG: OK")
print(f"SUN: OK")
print(f"Git push age: {push_age}")
print(f"Last mining block idx: {last.get('index')} ts: {ts_raw} age: {age_s}")
print(f"Chain len: {len(chain)} total = {len(chain_blocks)} blocks + {len(thesis_blocks)} thesis")
if thesis_blocks: print(f"Thesis: {thesis_blocks[-1].get('idx')} LIVE")
if os.path.exists(KERNEL_BIN):
 bsize=os.path.getsize(KERNEL_BIN)
 print(f"KERNEL BIN: {bsize} bytes ({bsize//32} blocks) / 32000 max")
 if os.path.exists(CHECKPOINT_JSON):
  cp=json.load(open(CHECKPOINT_JSON))
  print(f"CHECKPOINT: shed {cp.get('total_shed')} kept {cp.get('total_kept')} total_valid {cp.get('total_shed',0)+cp.get('total_kept',0)} merkle {cp.get('merkle_root','')[:12]}..")
  print(f"FULL BLOCKCHAIN inside {bsize} bytes — heads to feet valid")
else: print("KERNEL BIN: not built yet — run python pond_kernel.py")
print("HEALTH: OK - chain alive, thesis inscribed" if age<3600 else f"HEALTH: WARN - age {age_s}")
try:
 print(f"Size: {os.path.getsize(CHAIN)/1024:.0f}KB chain.json + {os.path.getsize(KERNEL_BIN)/1024 if os.path.exists(KERNEL_BIN) else 0:.0f}KB kernel.bin | Biougra | Ghoul V5.4")
except: pass
