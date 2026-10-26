import hashlib, json, time
from pathlib import Path
chain = Path("chain.json").read_bytes()
ch = hashlib.sha256(chain).hexdigest()
kh = hashlib.sha256(Path("pond.kernel.bin").read_bytes()).hexdigest()
j = json.loads(Path("chain.json").read_text())
head = j[-1]

print(f"=== EMBASSY PUSH ===")
print(f"Kernel: {kh[:16]} FULL {kh}")
print(f"Chain SHA256: {ch}")
print(f"HEAD: {head['idx']} kernel {head.get('kernel')} counts {len(j)}")
print()
print(f"ATTESTATION STRING:")
att = f"POND-Biougra-a13-HEAD-{head['idx']}-KERNEL-{kh[:16]}-CHAIN-{ch[:16]}-MOVED-{head.get('earth',{}).get('moved_m')}m-STAMP-12-34"
print(att)
print()

Path("/sdcard/POND/embassy").mkdir(parents=True, exist_ok=True)
emb = Path(f"/sdcard/POND/embassy/pond-HEAD-{head['idx']}-{kh[:8]}.json")
emb.write_bytes(chain)
Path(f"/sdcard/POND/embassy/ATTEST-{head['idx']}.txt").write_text(
    f"POND Count Biougra-a13 - OVERWRITTEN FORK\n"
    f"HEAD {head['idx']}\nKernel {kh}\nKernel_short {kh[:16]}\nChain {ch}\n"
    f"Counts {len(j)}\nMoved {head.get('earth',{}).get('moved_m')}m\n"
    f"Security: IBM lived RTC+earth+sun+kernel OVERWRITTEN d8377a4aa06d2c06\n"
    f"Stamp: 2026-05-16_12-34-00_graduation.txt inside ticker window 12:34 proof lived\n"
    f"Thesis 1453 anchor 00012fa8f9462bb8\n"
    f"Time: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n"
    f"Attestation: {att}\n"
)
print(f"Saved to {emb}")
