#!/usr/bin/env python3
import json, time
from datetime import datetime, timezone

print("=== POND Health v5.1-embassy-v2 b18f0c4 ===")
with open("chain.json") as f:
    c=json.load(f)
last=c[-1]
head=last["head"]

print(f"Chain: {len(c)} kept | LIVE {head} COUNT {head}")
print(f"Kernel: {last['kernel']} mono {last['mono']}")
print(f"Drift: {last['drift']:.2f} avg")
print(f"Live: {last['iso']} | {last['temp']}C | {last['bat']} | sun {last['sun']:.1f}")
print(f"Last: HEAD {head} | wall {last['wall_ts']} | age {time.time()-last['wall_ts']:.0f}s | glide {last['glide']:.2f}")
print(f"Window: boot {last['boot_elapsed']/3600:.2f}h ({last['boot_elapsed']:.0f}s)")
print(f"Build: b18f0c4 fb204d33->5594ad61 RAW signs WALL")
print(f"Time: {datetime.now(timezone.utc).isoformat()}")
print("=== OK ===")
