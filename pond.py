#!/usr/bin/env python3
import os, json, time, hashlib, math, subprocess, re, tempfile, signal
from datetime import datetime, timezone
from pathlib import Path

CHAIN = Path("chain.json")
STAMP_DIR = Path("/sdcard/POND/stamps")
STAMP_DIR.mkdir(parents=True, exist_ok=True)
KERNEL_FILE = Path("pond.kernel.bin")
LOCK_FILE = Path("/sdcard/POND/.pond.lock")
RUN_LOCK = Path("/sdcard/POND/.pond.run.lock")

def get_boottime():
    try:
        return float(open("/proc/uptime").read().split()[0])
    except:
        return time.monotonic()

def get_gps():
    try:
        j = json.loads(subprocess.check_output(["termux-location"], timeout=5).decode())
        return {"lat": float(j["latitude"]), "lon": float(j["longitude"]), "acc": float(j.get("accuracy", 99))}
    except:
        return {"lat": 30.263, "lon": -9.4, "acc": 9999}

def solar_az(lat, lon, utc_dt):
    try:
        day = utc_dt.timetuple().tm_yday
        decl = 23.45 * math.sin(math.radians(360/365*(284+day)))
        h = utc_dt.hour + utc_dt.minute/60.0
        ha = 15*(h-12)
        val = math.sin(math.radians(lat))*math.sin(math.radians(decl)) + math.cos(math.radians(lat))*math.cos(math.radians(decl))*math.cos(math.radians(ha))
        val = max(-1, min(1, val))
        return math.degrees(math.acos(val))
    except:
        return 0.0

def kernel_hash():
    try:
        return hashlib.sha256(KERNEL_FILE.read_bytes()).hexdigest()[:16]
    except:
        return "32K"

def load_chain_safe():
    if not CHAIN.exists():
        return []
    try:
        return json.loads(CHAIN.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"[RECOVER] chain.json corrupt: {e}")
        try:
            s = CHAIN.read_text(encoding='utf-8', errors='ignore')
            dec = json.JSONDecoder()
            obj, end = dec.raw_decode(s)
            bak = CHAIN.with_suffix(f".corrupt.{int(time.time())}.bak")
            CHAIN.rename(bak)
            print(f"[RECOVER] saved {bak} valid at {end} leftover {len(s)-end}")
            atomic_write_json(CHAIN, obj)
            return obj
        except Exception as e2:
            print(f"[RECOVER FAIL] {e2}")
            return []

def atomic_write_json(path: Path, obj):
    dirn = str(path.parent.absolute())
    fd, tmp = tempfile.mkstemp(dir=dirn, prefix=".chain.tmp.")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(obj, f, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try: os.remove(tmp)
            except: pass

def get_last_idx():
    chain = load_chain_safe()
    return int(chain[-1].get("idx", 1736)) if chain else 1736

def append_count(obj):
    if LOCK_FILE.exists():
        try:
            if time.time() - LOCK_FILE.stat().st_mtime > 60:
                LOCK_FILE.unlink()
        except:
            pass
    try:
        LOCK_FILE.write_text(str(os.getpid()))
        chain = load_chain_safe()
        chain.append(obj)
        atomic_write_json(CHAIN, chain)
        print(f"[saved] HEAD {obj['idx']} COUNT {len(chain)} atomic")
    finally:
        try: LOCK_FILE.unlink(missing_ok=True)
        except: pass

def parse_clock_from_name(name):
    m = re.search(r'(\d{2})[:-](\d{2})(?:[:-](\d{2}))?', name)
    if m:
        return f"{m.group(1)}:{m.group(2)}:{m.group(3) or '00'}"
    return None

def collect_stamps(s, e):
    out=[]
    for p in STAMP_DIR.iterdir():
        if not p.is_file(): continue
        try:
            mt = p.stat().st_mtime
            if s-1 <= mt <= e+1:
                clock = parse_clock_from_name(p.name) or datetime.fromtimestamp(mt).strftime("%H:%M:%S")
                out.append({"clock": clock, "precise_file_clock": parse_clock_from_name(p.name), "mtime_clock": datetime.fromtimestamp(mt).strftime("%H:%M:%S"), "utc": int(mt), "file": p.name, "hash": hashlib.sha256(p.read_bytes()).hexdigest()[:10]})
        except:
            pass
    return sorted(out, key=lambda x: x["utc"])

def handle_exit(signum, frame):
    print(f"\n[exit] {signum}")
    try: LOCK_FILE.unlink(missing_ok=True)
    except: pass
    try: RUN_LOCK.unlink(missing_ok=True)
    except: pass
    raise SystemExit

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# SINGLE INSTANCE CHECK
if RUN_LOCK.exists():
    try:
        age = time.time() - RUN_LOCK.stat().st_mtime
        if age < 3600:
            print(f"❌ Already running? {RUN_LOCK} age {age:.0f}s - kill old first with pkill -f pond.py")
            raise SystemExit(1)
        else:
            RUN_LOCK.unlink()
    except SystemExit:
        raise
    except:
        pass
RUN_LOCK.write_text(str(os.getpid()))

print("=== POND Count v2.2 atomic + tick + singleton ===")
last_idx = get_last_idx()
print(f"Kernel: {KERNEL_FILE} {kernel_hash()} 32K")
print(f"Chain: {CHAIN} HEAD {last_idx}")
print(f"Stamps: {STAMP_DIR}")

start_wall = time.time()
start_boot = get_boottime()
start_gps = get_gps()
start_sun = solar_az(start_gps["lat"], start_gps["lon"], datetime.now(timezone.utc))
print(f"Ticker OPEN {datetime.now().strftime('%H:%M:%S')} boot {start_boot:.0f}s")

while True:
    time.sleep(30)
    now_wall = time.time()
    now_boot = get_boottime()
    now_gps = get_gps()
    wd = now_wall - start_wall
    bd = now_boot - start_boot
    moved = math.hypot(now_gps["lat"]-start_gps["lat"], now_gps["lon"]-start_gps["lon"])*111320
    print(f"[tick] {datetime.now().strftime('%H:%M:%S')} wd {wd/60:.1f}m moved {moved:.0f}m boot {bd/60:.1f}m", flush=True)
    RUN_LOCK.write_text(str(os.getpid()))
    if abs(bd-wd) > 25:
        print(f"[skip] boot {bd:.0f} vs wall {wd:.0f} - doze, resync")
        start_wall = now_wall
        start_boot = now_boot
        continue
    close=False
    reason=""
    if moved>15000:
        close=True
        reason=f"moved {moved:.0f}m"
    elif wd>=2700:
        close=True
        reason="45m max"
    elif wd>=600 and moved<8:
        close=True
        reason=f"{int(wd/60)}m stable"
    if close:
        now_sun = solar_az(now_gps["lat"], now_gps["lon"], datetime.now(timezone.utc))
        stamps = collect_stamps(start_wall, now_wall)
        new_idx = last_idx+1
        obj = {"idx": new_idx, "count": new_idx, "version": 2, "ticker_window": {"start": datetime.fromtimestamp(start_wall).strftime("%Y-%m-%d %H:%M:%S"), "end": datetime.fromtimestamp(now_wall).strftime("%Y-%m-%d %H:%M:%S"), "wall_delta": int(wd), "boot_delta": int(bd)}, "earth": {"start": start_gps, "end": now_gps, "moved_m": int(moved)}, "sun": {"start": round(start_sun,2), "end": round(now_sun,2), "delta": round(now_sun-start_sun,3)}, "kernel": kernel_hash(), "stamps": stamps, "security": "IBM lived RTC+earth+sun+kernel", "reason": reason}
        append_count(obj)
        print(f"\n>>> POND Count {new_idx} CLOSED {reason} lived {int(bd)}s stamps {len(stamps)}")
        for s in stamps:
            print(f"  - {s['clock']} {s['file']}")
        print(f">>> OPEN {datetime.now().strftime('%H:%M:%S')}\n")
        last_idx=new_idx
        start_wall=now_wall
        start_boot=now_boot
        start_gps=now_gps
        start_sun=now_sun
