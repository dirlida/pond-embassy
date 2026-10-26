import os, hashlib, time, math
from pathlib import Path

def get_boot():
    try:
        with open("/proc/uptime") as f:
            return f.read()
    except:
        return str(time.monotonic())

seed = f"{time.time()}{os.urandom(32)}{get_boot()}"
h = hashlib.sha256(seed.encode()).digest()
out = b""
while len(out) < 32768:
    h = hashlib.sha256(h + os.urandom(32)).digest()
    out += h

out = out[:32768]
Path("pond.kernel.bin").write_bytes(out)
print(f"NEW KERNEL 32K {hashlib.sha256(out).hexdigest()[:16]}")
print(f"FULL SHA256 {hashlib.sha256(out).hexdigest()}")
print(f"SIZE {len(out)}")
