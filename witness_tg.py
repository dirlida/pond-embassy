import json, time, os, socket, requests
orig = socket.getaddrinfo
socket.getaddrinfo = lambda *a, **k: [r for r in orig(*a, **k) if r[0]==socket.AF_INET]
BOT_TOKEN=os.getenv("TG_BOT_TOKEN")
CHAT_ID=os.getenv("TG_CHAT_ID")
last_sent=None
while True:
    try:
        with open("chain.json") as f: chain=json.load(f)
        last=chain[-1]
        p=last.get("payload", last)
        idx=p.get("index", len(chain)-1)
        if idx==last_sent:
            time.sleep(30)
            continue
        pondId=str(last.get("pondId") or last.get("hash") or p.get("pondId",""))[:12]
        btc=p.get("btcHeight","?")
        sun=p.get("sunAltitude",15.2)
        merkle=str(p.get("merkle_root",""))[:16]
        txt=f"""● POND {len(chain)} total = {len(chain)-1} blocks + 1 thesis LIVE
idx {idx} id {pondId}.. btc {btc} anchor LIVE
sun {sun} merkle {merkle}..
drift -6 SLOW ATTESTED 4x
thesis 1453 LIVE | Ghoul V5.4 Biougra
https://dirlida.github.io/pond-embassy/"""
        r=requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id":CHAT_ID,"text":txt}, timeout=20)
        print(f"TG {r.status_code} idx {idx}", flush=True)
        if r.ok: last_sent=idx
    except Exception as e:
        print(f"err {e}", flush=True)
        time.sleep(10)
    time.sleep(30)
