# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
import time, json, os, hashlib, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

CHAIN_FILE="chain.json"; DRIFT_FILE="drift.json"; LIVE_FILE="live.json"; KERNEL_FILE="pond.kernel.bin"; TEMP_CSV="temp_drift.csv"; LOG_DIR="stamps"; INTERVAL=600; TEMP_CACHE_SEC=30; CSV_EVERY_SEC=300
VERSION="v4.4.3-TCXO-PID-SEIKO-STABLE"; KERNEL_HEX="fbcbad2c5324f560"

TEMP_COEFF_MS_PER_C = 3.953
BASE_TEMP = 39.5
BASE_DRIFT_MS = 1.2268461287021637
KP, KI, KD = 0.12, 0.008, 0.02

Path(LOG_DIR).mkdir(exist_ok=True)
if not os.path.exists(TEMP_CSV):
    open(TEMP_CSV,"w").write("ts,iso,temp,drift_raw,drift_corr,boot,wall,glide,sun,earth,bat_status,mono_kernel\n")

def get_bat():
    try:
        out=subprocess.check_output(["termux-battery-status"], timeout=5).decode()
        j=json.loads(out)
        return j, j.get("status","UNKNOWN"), j.get("percentage",0), float(j.get("temperature",38.8))
    except:
        return None, "UNKNOWN", 0, 38.8

def load_json(f, default):
    try:
        with open(f) as fp: return json.load(fp)
    except: return default

def save_json(f, data):
    with open(f,"w") as fp: json.dump(data, fp, indent=2)

def get_mono_kernel():
    try:
        if os.path.exists(KERNEL_FILE):
            return hashlib.sha256(open(KERNEL_FILE,"rb").read()).hexdigest()[:16]
    except: pass
    return KERNEL_HEX

raw_drift=load_json(DRIFT_FILE,{})
drift={
    "avg": raw_drift.get("avg", raw_drift.get("drift", 13.08)),
    "corr": raw_drift.get("corr", BASE_DRIFT_MS),
    "raw_last": raw_drift.get("raw_last", 13.08),
    "integral": raw_drift.get("integral",0.0),
    "prev_error": raw_drift.get("prev_error",0.0),
    "last_mono": None,
    "last_wall": None,
    "last_temp": raw_drift.get("last_temp",38.8),
    "samples": raw_drift.get("samples",2)
}

chain=load_json(CHAIN_FILE,[])
boot_start_mono=time.monotonic(); boot_start_wall=time.time()
last_csv_write=boot_start_wall-350
last_temp=38.8; last_temp_t=0
last_raw_update=time.time()

def correct_drift(raw_ms, temp_c, sun_val):
    temp_err = temp_c - BASE_TEMP
    temp_corrected = raw_ms + (temp_err * TEMP_COEFF_MS_PER_C * 0.1) # reduced coeff, 10% only for slow correction
    sun_factor = (sun_val - 50) * 0.001
    sun_corrected = temp_corrected + sun_factor
    # HARD CLAMP positive 0.05ms to 15ms
    corrected = max(0.05, min(15.0, sun_corrected))
    return corrected, temp_corrected

print(f"POND {VERSION} kernel {get_mono_kernel()} drift raw {drift['avg']:.3f} corr {drift['corr']:.3f} chain {len(chain)} START {datetime.now(timezone.utc).isoformat()}", flush=True)

while True:
    try:
        now_wall=time.time(); now_mono=time.monotonic()
        boot_elapsed=now_mono-boot_start_mono; wall_elapsed=now_wall-boot_start_wall

        if now_wall-last_temp_t> TEMP_CACHE_SEC:
            _, _, _, t = get_bat()
            last_temp=t; last_temp_t=now_wall
        temp=last_temp
        _, status, pct, _ = get_bat()
        sun=(boot_elapsed/3600.0)*15.0%360.0; earth=0
        
        # FIXED: only recompute raw every INTERVAL, with EMA filter
        raw_now = drift["avg"]
        if now_wall - last_raw_update >= INTERVAL:
            if drift["last_mono"] is not None and drift["last_wall"] is not None:
                dt_mono = now_mono - drift["last_mono"]
                dt_wall = now_wall - drift["last_wall"]
                if dt_wall > 300: # need 5min min for stable measure
                    measured = (dt_mono - dt_wall)/dt_wall*1000.0
                    # EMA filter 0.2 new 0.8 old to kill noise
                    raw_now = drift["avg"]*0.8 + measured*0.2
                    # clamp measured raw to sane -10 to +20ms
                    raw_now = max(-10.0, min(20.0, raw_now))
            last_raw_update = now_wall
            drift["last_mono"]=now_mono
            drift["last_wall"]=now_wall
        
        # if first boot, init last markers
        if drift["last_mono"] is None:
            drift["last_mono"]=now_mono
            drift["last_wall"]=now_wall

        drift_corr, temp_corr = correct_drift(raw_now, temp, sun)
        
        error = raw_now - drift_corr
        drift["integral"] = max(-5, min(5, drift["integral"] + error*KI))
        derivative = error - drift["prev_error"]
        glide_pid = KP*error + drift["integral"] + KD*derivative
        drift["prev_error"] = error
        glide=(drift_corr/1000.0/3600.0)*boot_elapsed + glide_pid/1000.0

        drift["raw_last"]=raw_now
        drift["corr"]=drift_corr
        # don't overwrite avg until next interval - keep stable
        # drift["avg"]=raw_now

        if now_wall-last_csv_write>=CSV_EVERY_SEC:
            iso=datetime.now(timezone.utc).isoformat(); mono_k=get_mono_kernel()
            line=f"{int(now_wall)},{iso},{temp:.1f},{raw_now:.3f},{drift_corr:.3f},{boot_elapsed:.0f},{wall_elapsed:.0f},{glide:.6f},{sun:.2f},{earth},{status}_{pct},{mono_k}\n"
            with open(TEMP_CSV,"a") as f: f.write(line)
            drift["last_temp"]=temp
            drift["avg"]=raw_now
            save_json(DRIFT_FILE, drift)
            print(f"CSV {temp:.1f}C raw {raw_now:.3f} corr {drift_corr:.3f} glide {glide:.6f} pid {glide_pid:.4f}", flush=True)

        if len(chain)==0 or now_wall-chain[-1].get("wall_ts",0)>=INTERVAL:
            head_n=chain[-1]["head"]+1 if len(chain)>0 and "head" in chain[-1] else 2094
            try:
                lo=load_json(LIVE_FILE,{})
                if lo.get("LIVE",0)>=head_n: head_n=lo["LIVE"]+1
            except: pass
            block={"head":head_n,"wall_ts":now_wall,"iso":datetime.now(timezone.utc).isoformat(),"boot_elapsed":boot_elapsed,"wall":wall_elapsed,"drift_raw":raw_now,"drift":drift_corr,"drift_corr":drift_corr,"temp":temp,"glide":glide,"glide_pid":glide_pid,"sun":sun,"earth":earth,"kernel":get_mono_kernel(),"mono":get_mono_kernel(),"version":VERSION,"bat":f"{status}_{pct}"}
            chain.append(block)
            if len(chain)>100: chain=chain[-100:]
            save_json(CHAIN_FILE, chain)
            live={"LIVE":head_n,"COUNT":head_n,"KERNEL":get_mono_kernel(),"mono":get_mono_kernel(),"time":block["iso"],"stamps":0,"log":f"{os.path.getsize('pond.log') if os.path.exists('pond.log') else 0}b","earth":f"{earth}m","sun":f"{sun:.1f}","version":VERSION,"drift":f"{drift_corr:.3f}","drift_raw":f"{raw_now:.3f}","temp":f"{temp:.1f}","bat":f"{status}_{pct}"}
            save_json(LIVE_FILE, live)
            print(f"CLOSED HEAD {head_n} raw {raw_now:.3f} corr {drift_corr:.3f} temp {temp:.1f}C", flush=True)
        time.sleep(10)
    except Exception as e:
        print(f"ERR {e}", file=sys.stderr, flush=True); import traceback; traceback.print_exc(); time.sleep(5)
