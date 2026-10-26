import json, re
from pathlib import Path
p = Path("chain.json")
txt = p.read_text(errors="ignore")
# extract all objects with idx or index
objs = []
# find {...} blocks
for m in re.finditer(r'\{[^{}]*"idx"\s*:\s*\d+[^{}]*\}| \{"idx".*?\n\}', txt, re.DOTALL):
    try:
        o = json.loads(m.group(0))
        if "idx" in o:
            objs.append(o)
    except:
        pass
# also parse if file is almost valid json array
try:
    data = json.loads(txt)
    if isinstance(data, list):
        # filter only v2
        v2 = [x for x in data if isinstance(x, dict) and "idx" in x]
        objs = v2
except:
    pass

# fallback: regex for idx
if not objs:
    for m in re.finditer(r'"idx"\s*:\s*(\d+)', txt):
        pass

# dedup by idx, keep last
uniq = {}
for o in objs:
    uniq[o["idx"]] = o

# also need to recover from .bak or embassy? Keep what we have
sorted_chain = sorted(uniq.values(), key=lambda x: x["idx"])
# save
Path("chain.json.broken").write_bytes(p.read_bytes())
Path("chain.json").write_text(json.dumps(sorted_chain, indent=2))
print(f"Fixed: {len(sorted_chain)} counts HEAD {sorted_chain[-1]['idx'] if sorted_chain else 'empty'}")
print(f"Old kernel 60b812... should be 1737, new kernel d8377... from 1738")
for c in sorted_chain[-5:]:
    print(f" - {c['idx']} kernel {c.get('kernel')} reason {c.get('reason')}")
