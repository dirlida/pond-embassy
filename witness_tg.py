import json, time, os, socket, requests
orig = socket.getaddrinfo
socket.getaddrinfo = lambda *a, **k: [r for r in orig(*a, **k) if r[0]==socket.AF_INET]

BOT_TOKEN=os.getenv("TG_BOT_TOKEN")
CHAT_ID=os.getenv("TG_CHAT_ID")

last_sent=None
while True:
    try:
        with open("chain.json") as f:
            chain=json.load(f)
        last=chain[-1]
        idx=last.get("idx", len(chain)-1)
        if idx==last_sent:
            time.sleep(30)
            continue

        kernel=last.get("kernel","?")
        kernel_full=last.get("kernel_full", kernel)
        moved=last.get("earth",{}).get("moved_m",0)
        stamps=last.get("stamps",[])
        reason=last.get("reason","lived")
        ticker=last.get("ticker_window",{})
        wd=ticker.get("wall_delta",0)
        sun=last.get("sun",{})
        
        stamp_txt = ""
        if stamps:
            s=stamps[0]
            stamp_txt = f"stamp {s.get('precise_file_clock','?')} {s.get('file','')[:20]}"

        txt=f"""● POND OVERWRITTEN LIVE {len(chain)} total = {len(chain)-1} counts + 1 thesis
HEAD {idx} kernel {kernel} 32K
moved {moved:.0f}m wall {wd:.0f}s {reason}
{stamp_txt}
sun {sun.get('start','?')}->{sun.get('end','?')} lived RTC
thesis 1453 anchor 00012fa8 LIVE | Ghoul V5.4 Biougra
every bit overwritten d8377a4aa06d2c06
https://dirlida.github.io/pond-embassy/"""

        r=requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id":CHAT_ID,"text":txt}, timeout=20)
        print(f"TG {r.status_code} idx {idx} kernel {kernel} -> {r.text[:100]}", flush=True)
        if r.ok:
            last_sent=idx
    except Exception as e:
        print(f"err {e}", flush=True)
        time.sleep(10)
    time.sleep(30)
