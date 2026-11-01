# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
import time, json, os, hashlib, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

CHAIN_FILE="chain.json"; DRIFT_FILE="drift.json"; LIVE_FILE="live.json"; KERNEL_FILE="pond.kernel.bin"; TEMP_CSV="temp_drift.csv"; LOG_DIR="stamps"; INTERVAL=600; TEMP_CACHE_SEC=30; CSV_EVERY_SEC=300
VERSION="v5.1-embassy-v2-VERIFIER"; KERNEL_HEX="00acc019a757aae6"

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

def write_index(head, live, drift_avg):
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name=viewport content="width=device-width,initial-scale=1">
<title>POND {head}</title>
<style>
body{{margin:0;background:#0a0a0b;color:#e8e6e1;font-family:ui-monospace,Menlo,monospace;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}}
.wrap{{width:100%;max-width:520px}}.card{{background:#15151a;border:1px solid #24242f;border-radius:22px;padding:22px 20px}}
.head{{font-size:52px;font-weight:900;letter-spacing:-1.5px;color:#f5d36c;line-height:1}}
.sub{{margin-top:8px;font-size:13px;color:#9a9aa3}}.row{{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}}
.chip{{background:#1c1c22;border:1px solid #2b2b36;border-radius:999px;padding:8px 13px;font-size:12px;color:#b8b8c0}} .chip b{{color:#fff;font-weight:700}}
.live{{margin-top:16px;background:#0f0f12;border:1px solid #222;border-radius:14px;padding:14px;font-size:11px;line-height:1.6;white-space:pre-wrap;color:#c8c8d0;max-height:420px;overflow:auto}}
.ok{{color:#4ade80;font-weight:800}} .footer{{margin-top:14px;font-size:11px;color:#555;text-align:center}} a{{color:#7afcff;text-decoration:none}}
</style></head><body>
<div class=wrap><div class=card>
<div class=head>HEAD {head}</div>
<div class=sub><span class=ok>=== OK ===</span> • LIVE {head} COUNT {head} • {VERSION}</div>
<div class=row>
<span class=chip>Kernel <b>{get_mono_kernel()}</b></span>
<span class=chip>Drift <b>{drift_avg:.2f} avg</b></span>
<span class=chip>Chain <b>100 kept</b></span>
</div>
<div class=row>
<span class=chip>Build <b>b18f0c4</b></span>
<span class=chip>Wall <b>{datetime.now(timezone.utc).isoformat()}</b></span>
<span class=chip>Boot <b>{live.get("boot","-")}</b></span>
</div>
<div class=live id=live>Loading chain.json...</div>
</div>
<div class=footer>pond-embassy • {get_mono_kernel()} • <a href="chain.json">chain.json</a> • <a href="live.json">live.json</a></div>
</div>
<script>
async function load(){{try{{let [lv,ch]=await Promise.all([fetch('live.json?v='+Date.now()).then(r=>r.json()).catch(()=>null),fetch('chain.json?v='+Date.now()).then(r=>r.text()).catch(()=>null)]);let t=`HEAD {head} COUNT {head}\\nKernel {get_mono_kernel()}\\nDrift {drift_avg:.2f}\\nBuild b18f0c4\\n\\n`;if(lv) t+=JSON.stringify(lv,null,2).slice(0,1200)+"\\n\\n";if(ch) t+=ch.slice(0,1200);document.getElementById('live').textContent=t;}}catch(e){{}}
}}
load(); setInterval(load,5000);
</script>
</body></html>"""
    with open("index.html","w") as out: out.write(html)
    if Path("docs").exists():
        with open("docs/index.html","w") as out: out.write(html)

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
boot_start_mono=time.monotonic(); boot_start_wall=time.time(); last_csv_write=boot_start_wall-350
last_temp=38.8; last_temp_t=0; last_raw_update=time.time()

def correct_drift(raw_ms, temp_c, sun_val):
    temp_err = temp_c - BASE_TEMP
    temp_corrected = raw_ms + (temp_err * TEMP_COEFF_MS_PER_C * 0.1)
    sun_factor = (sun_val - 50) * 0.001
    sun_corrected = temp_corrected + sun_factor
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
        raw_now = drift["avg"]
        if now_wall - last_raw_update >= INTERVAL:
            if drift["last_mono"] is not None and drift["last_wall"] is not None:
                dt_mono = now_mono - drift["last_mono"]
                dt_wall = now_wall - drift["last_wall"]
                if dt_wall > 300:
                    measured = (dt_mono - dt_wall)/dt_wall*1000.0
                    raw_now = drift["avg"]*0.8 + measured*0.2
                    raw_now = max(-10.0, min(20.0, raw_now))
            last_raw_update = now_wall
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
        if now_wall-last_csv_write>=CSV_EVERY_SEC:
            iso=datetime.now(timezone.utc).isoformat(); mono_k=get_mono_kernel()
            line=f"{int(now_wall)},{iso},{temp:.1f},{raw_now:.3f},{drift_corr:.3f},{boot_elapsed:.0f},{wall_elapsed:.0f},{glide:.6f},{sun:.2f},{earth},{status}_{pct},{mono_k}\n"
            with open(TEMP_CSV,"a") as f: f.write(line)
            drift["last_temp"]=temp
            drift["avg"]=raw_now
            last_csv_write=now_wall
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
            live={"LIVE":head_n,"COUNT":head_n,"HEAD":head_n,"KERNEL":get_mono_kernel(),"mono":get_mono_kernel(),"time":block["iso"],"boot":f"{boot_elapsed/3600:.1f}h","earth":f"{earth}m","sun":f"{sun:.1f}","version":VERSION,"drift":f"{drift_corr:.3f}","drift_raw":f"{raw_now:.3f}","temp":f"{temp:.1f}","bat":f"{status}_{pct}"}
            save_json(LIVE_FILE, live)
            write_index(head_n, live, drift_corr)
            print(f"CLOSED HEAD {head_n} raw {raw_now:.3f} corr {drift_corr:.3f} temp {temp:.1f}C - index rebuilt", flush=True)
        time.sleep(10)
    except Exception as e:
        print(f"ERR {e}", file=sys.stderr, flush=True); import traceback; traceback.print_exc(); time.sleep(5)
