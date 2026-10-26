import json, re
from pathlib import Path
txt = Path("chain.json.broken").read_bytes().decode(errors="ignore")
# Try to load as json array if possible ignoring tail errors
# The broken file is mixed - let's extract both v1 index and v2 idx

objs_v2 = []
# extract all v2 blocks with balanced braces via simple scan
# crude but work: split by "}\n,  {" etc
parts = re.split(r'\},\s*\{', txt)
for part in parts:
    if '"idx"' in part:
        try:
            # add braces back
            if not part.strip().startswith("{"):
                part = "{" + part
            if not part.strip().endswith("}"):
                part = part + "}"
            o = json.loads(part)
            if "idx" in o:
                objs_v2.append(o)
        except:
            pass

print(f"found v2: {len(objs_v2)}")

# Now also try to get original chain from git or backup?
# If you have chain.json from earlier backups, list:
for p in Path(".").glob("*.bak*"):
    print(p)

# Keep best v2 sorted
uniq = {o["idx"]: o for o in objs_v2}
sorted_v2 = sorted(uniq.values(), key=lambda x: x["idx"])
Path("chain.json").write_text(json.dumps(sorted_v2, indent=2))
print(f"restored HEAD {sorted_v2[-1]['idx'] if sorted_v2 else 0} count {len(sorted_v2)}")
for c in sorted_v2[-10:]:
    print(c["idx"], c.get("kernel"), c.get("reason",""))
