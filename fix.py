import pathlib, re
# restore from original template if you have it in repo
text=pathlib.Path("pond.py").read_text()
# fix the broken continue(( line
text=text.replace(" continue((b.get('index',0)", " curr_index=max((b.get('index',0)")
# also ensure while loop structure
# Remove duplicate curr_index line if present twice
lines=text.splitlines()
out=[]
seen_curr=False
for l in lines:
    if 'elapsed=now-prev_time' in l and not seen_curr:
        out.append(l)
        if not any('curr_index=max' in x for x in out[-3:]):
            out.append(' curr_index=max((b.get("index",0) for b in chain if isinstance(b.get("index"),int)), default=0)+1')
        seen_curr=True
    elif 'curr_index=max((b.get' in l:
        if seen_curr and l.strip().startswith('curr_index=max') and out[-1].strip().startswith('curr_index=max'):
            continue
        # keep only first after elapsed
        if out and out[-1].strip().startswith('curr_index=max'):
            # skip second
            continue
        out.append(l)
        seen_curr=True
    else:
        out.append(l)

# ensure 10MIN RULE uses curr_index+1 but after definition
fixed="\n".join(out)
pathlib.Path("pond.py").write_text(fixed)
print("manual fixed")
