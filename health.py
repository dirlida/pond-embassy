#!/usr/bin/env python3
import json, hashlib, time
from pathlib import Path

CHAIN = Path("chain.json")
KERNEL = Path("pond.kernel.bin")
STAMP_DIR = Path("/sdcard/POND/stamps")
LOCK_FILE = Path("/sdcard/POND/.pond.lock")

def kernel_hash():
    try:
        return hashlib.sha256(KERNEL.read_bytes()).hexdigest()
    except:
        return "missing"

def check_chain():
    if LOCK_FILE.exists():
        try:
            age = time.time() - LOCK_FILE.stat().st_mtime
            if age > 60:
                LOCK_FILE.unlink()
                print(f"[lock] cleared stale {age:.0f}s")
            else:
                print(f"⚠️ WRITE IN PROGRESS {age:.0f}s old - retry 2s")
                time.sleep(2)
                if LOCK_FILE.exists():
                    print("⚠️ still locked - reading anyway (atomic safe)")
        except Exception as e:
            print(f"[lock check fail] {e}")

    print("=== POND HEALTH ===")
    kh = kernel_hash()
    print(f"Kernel: {KERNEL} {kh[:16]} {kh} SIZE {KERNEL.stat().st_size if KERNEL.exists() else 0}")

    try:
        data = json.loads(CHAIN.read_text())
    except Exception as e:
        print(f"❌ chain.json invalid: {e}")
        return

    print(f"Chain: {CHAIN} COUNT {len(data)} HEAD {data[-1].get('idx') if data else 'empty'}")

    thesis = [c for c in data if c.get("idx")==1453]
    if thesis:
        print(f"✅ Thesis 1453 anchor {thesis[0].get('anchor_hash')[:16] if thesis[0].get('anchor_hash') else 'no hash'}")

    v2 = [c for c in data if c.get("version")==2]
    for c in v2[-5:]:
        idx = c.get("idx")
        k = c.get("kernel","?")
        reason = c.get("reason","")
        stamps = c.get("stamps",[])
        moved = c.get("earth",{}).get("moved_m",0)
        if idx==1737:
            if k in ("d8377a4aa06d2c06","fbcbad2c5324f560"):
                print(f"✅ {idx} NEW KERNEL {k} {reason} moved {moved}m stamps {len(stamps)}")
            else:
                print(f"⚠️  {idx} OLD KERNEL {k} expected d8377a/fbcbad2c")
        else:
            print(f"  {idx} kernel {k} {reason}")

    if STAMP_DIR.exists():
        stamps = list(STAMP_DIR.iterdir())
        print(f"Stamps dir: {STAMP_DIR} {len(stamps)} files")
        for p in stamps[-5:]:
            print(f"  - {p.name} mtime {time.ctime(p.stat().st_mtime)}")
    else:
        print(f"❌ Stamps dir missing {STAMP_DIR}")

    try:
        with open("/proc/uptime") as f:
            boot = float(f.read().split()[0])
        print(f"✅ RTC boot {boot:.0f}s {boot/3600:.1f}h lived - IBM check")
    except:
        print(f"⚠️  /proc/uptime blocked - using monotonic {time.monotonic():.0f}s")

    if data and data[-1].get("kernel")==kh[:16]:
        print(f"\n✅ HEALTH OK - HEAD {data[-1]['idx']} matches live kernel {kh[:16]} - POND lived ticking")
    else:
        live = kh[:16]
        head_k = data[-1].get('kernel') if data else 'empty'
        head_idx = data[-1].get('idx') if data else 0
        print(f"\n⚠️  HEALTH FORK - chain HEAD {head_idx} kernel {head_k} != live {live} - will sync on next {head_idx+1}")

    next_idx = (data[-1].get('idx', 1737)+1) if data else 1738
    print(f"\nNext: pond.py will close {next_idx} with kernel {kh[:16]} when moved 35m or 10-45m stable")

if __name__=="__main__":
    check_chain()
