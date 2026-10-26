#!/usr/bin/env python3
# POND health - no hardcoded HEAD, reads live chain.json
import json, os, glob, time, pathlib

p = pathlib.Path(__file__).parent
chain_path = p / "chain.json"
log_path = p / "pond.log"
stamps_path = p / "stamps"

print("POND health")
print("="*40)

# chain
if chain_path.exists():
    try:
        data = json.loads(chain_path.read_text()[-20000:]) if chain_path.stat().st_size < 500000 else json.loads(chain_path.read_text().split('{"head"')[-1])
        # try full load, fallback to tail parse
    except:
        try:
            data = json.loads(chain_path.read_text())
        except Exception as e:
            data = None
            print(f"chain.json read error: {e}")

    if data:
        # supports both {"HEAD":...} and {"chain":[...]}
        head = data.get("HEAD") or data.get("head") or (data.get("chain", [{}])[-1].get("head") if data.get("chain") else "unknown")
        count = data.get("COUNT") or data.get("count") or len(data.get("chain", []))
        kernel = data.get("KERNEL") or data.get("kernel") or data.get("chain", [{}])[-1].get("kernel") if data.get("chain") else "unknown"
        print(f"chain.json: {chain_path.stat().st_size} bytes")
        print(f"HEAD: {head}")
        print(f"COUNT: {count}")
        print(f"KERNEL: {kernel}")
        # last bead time
        try:
            chain = data.get("chain", [])
            if chain:
                last = chain[-1]
                print(f"last mono: {last.get('mono')}")
                print(f"last time: {last.get('time')}")
        except:
            pass
else:
    print("chain.json not found")

# stamps
if stamps_path.exists():
    files = sorted(glob.glob(str(stamps_path/"*")))
    print(f"\nstamps/: {len(files)} files")
    if files:
        print(f"latest: {os.path.basename(files[-1])}")
        # check age
        age = time.time() - os.path.getmtime(files[-1])
        print(f"latest age: {int(age)}s ago")
else:
    print("\nstamps/ not found")

# log
if log_path.exists():
    size = log_path.stat().st_size
    print(f"\npond.log: {size} bytes")
    try:
        lines = log_path.read_text().strip().splitlines()[-5:]
        print("tail:")
        for l in lines:
            print(f"  {l[-120:]}")
    except:
        pass
else:
    print("\npond.log not found")

# process check via lock file or pid
lock = pathlib.Path("/tmp/pond.lock") if pathlib.Path("/tmp/pond.lock").exists() else p / "pond.lock"
if lock.exists() or pathlib.Path(os.environ.get("TMPDIR","/tmp")+"/pond.lock").exists():
    print(f"\nlock: present")
else:
    print(f"\nlock: not found (check ps)")

print("="*40)

# -- export live.json --
if __name__ == "__main__" and "--json" in __import__("sys").argv:
    import json, pathlib
    p = pathlib.Path(__file__).parent
    cp = p / "chain.json"
    try:
        d = json.loads(cp.read_text())
        chain = d.get("chain", [])
        last = chain[-1] if chain else {}
        out = {
            "HEAD": d.get("HEAD") or last.get("head"),
            "COUNT": d.get("COUNT") or len(chain),
            "KERNEL": d.get("KERNEL") or last.get("kernel"),
            "mono": last.get("mono"),
            "time": last.get("time"),
            "stamps": len(list((p/"stamps").glob("*"))),
            "log_bytes": (p/"pond.log").stat().st_size if (p/"pond.log").exists() else 0
        }
        (p/"live.json").write_text(json.dumps(out, indent=2))
        print("\nlive.json written")
    except Exception as e:
        print(f"json export fail {e}")
