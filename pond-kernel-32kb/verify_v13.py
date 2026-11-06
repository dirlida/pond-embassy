import hashlib, struct
data = open("pond-32k.bin","rb").read()
print(f"size: {len(data)} / 32768")
print(f"sha256: {hashlib.sha256(data).hexdigest()}")
print("PASS size" if len(data) <= 32768 else "FAIL size")
for bad in [b"wallet", b"secp256k1", b"bech32", b"base58", b"ed25519"]:
    print(f"{'FAIL' if bad in data else 'PASS'} no {bad.decode()} in kernel")
# correct offset: pond_journal addr - base addr
off = 1072816 - 1048576  # 24240
head = struct.unpack("<Q", data[off:off+8])[0]
print(f"last_sealed_head at offset {off}: {head} {'PASS' if head==2804 else 'FAIL'}")
# dump all 5 u64 in pond_journal
vals = struct.unpack("<5Q", data[off:off+40])
print(f"pond_journal 5x u64: {vals}")
