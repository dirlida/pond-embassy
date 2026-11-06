#!/usr/bin/env python3
# POND daemon v13 - OFFLINE, stdlib only
import hashlib, struct, json, os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KERNEL = os.path.join(BASE_DIR, "c-kernel", "pond-32k.bin")
EXPECTED_SHA = "c50f58a7e28932eda3fc9ab8a1c1cb690ba9f865abfb8cd00d98336cab81c4ff"
BASE = 0x00100000
JOURNAL_ADDR = 1072816

def verify_kernel(path=KERNEL):
    data = open(path, "rb").read()
    sha = hashlib.sha256(data).hexdigest()
    assert len(data) <= 32768, f"SIZE FAIL {len(data)}"
    assert sha == EXPECTED_SHA, f"SHA FAIL {sha}"
    for bad in [b"wallet", b"secp256k1", b"bech32", b"base58", b"ed25519"]:
        assert bad not in data, f"WALLET LEAK: {bad}"
    off = JOURNAL_ADDR - BASE
    head, h0, h1, h2, h3, nvm_writes, rtc_mirror, gap_total = struct.unpack("<8Q", data[off:off+64])
    return {
        "size": len(data),
        "sha256": sha,
        "last_sealed_head": head,
        "chain_hash": [h0, h1, h2, h3],
        "nvm_write_count": nvm_writes,
        "last_rtc_mirror": rtc_mirror,
        "gap_total_mirror": gap_total,
        "verified": True,
    }

def attest():
    info = verify_kernel()
    print(json.dumps(info, indent=2))
    return info

if __name__ == "__main__":
    attest()
