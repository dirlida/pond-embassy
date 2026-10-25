#!/data/data/com.termux/files/usr/bin/python3
import json, struct, hashlib, os
KERNEL_BIN="pond.kernel.bin"
CHECKPOINT_JSON="pond.checkpoint.json"
CHAIN_JSON="chain.json"
FMT=">Hhbb26s"
SIZE=32
MAXB=1000
def h26(s):
 s=str(s)
 c="".join(x for x in s if x in "0123456789abcdefABCDEF")[:52].ljust(52,"0")
 try: return bytes.fromhex(c)
 except: return s.encode()[:26].ljust(26,b'\0')
def get_btc(b, fallback):
 try:
  v=b.get("payload",{}).get("btcHeight", fallback)
  if v is None: return fallback
  return int(v)
 except: return fallback
def build():
 print("[ONE RUN] loading chain.json...")
 with open(CHAIN_JSON,"r") as f:
  chain=json.load(f)
  if isinstance(chain, dict): chain=chain.get("blocks",[])
 total=len(chain)
 print(f"Loaded {total}")
 to_shed=chain[:-MAXB] if total>MAXB else []
 to_keep=chain[-MAXB:] if total>MAXB else chain
 merkle=hashlib.sha256(b"POND_GENESIS_V1").digest()
 for b in to_shed:
  merkle=hashlib.sha256(merkle+h26(b.get("hash",""))).digest()
 btc_start=get_btc(to_shed[0], 969609) if to_shed else get_btc(chain[0], 969609) if chain else 972583
 btc_end=get_btc(to_shed[-1], btc_start) if to_shed else btc_start
 cp={"start_idx":to_shed[0].get("index",0) if to_shed else 0,"end_idx":to_shed[-1].get("index",-1) if to_shed else -1,"merkle_root":merkle.hex(),"btc_start":btc_start,"btc_end":btc_end,"total_shed":len(to_shed),"total_kept":len(to_keep),"total_chain":total,"thesis":"1453 LIVE"}
 with open(CHECKPOINT_JSON,"w") as f: json.dump(cp,f,indent=2)
 with open(KERNEL_BIN,"wb") as out:
  prev=btc_end
  c=0
  for b in to_keep:
   idx=int(b.get("index",0) or 0)%65536
   btc=get_btc(b, prev)
   d=max(-32768,min(32767,btc-prev))
   try: sun=float(b.get("payload",{}).get("sunAltitude",15.2) or 15.2)
   except: sun=15.2
   sun_i=max(-128,min(127,int(sun*10)))
   out.write(struct.pack(FMT,idx,d,sun_i,-6,h26(b.get("hash",""))))
   prev=btc
   c+=1
   if c%200==0: print(f"  wrote {c}/{len(to_keep)}")
 print(f"[DONE] {KERNEL_BIN}={os.path.getsize(KERNEL_BIN)} bytes = {len(to_keep)}*32")
 print(f"[DONE] shed {len(to_shed)} merkle {merkle.hex()[:16]}")
 print(f"[SAFE] {CHAIN_JSON}={os.path.getsize(CHAIN_JSON)} bytes untouched")
 print(f"FULL CHAIN inside 32KB: {len(to_shed)}+{len(to_keep)}={total}")
if __name__=="__main__": build()
