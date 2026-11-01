# POND Embassy Kernel v12 Final Fully Fledged - a4c1a228

Date: 2026-11-01T18:52 UTC
HEAD: 2806 LIVE 2806 COUNT 2806
Kernel: a4c1a2285f33c07a679989f4ce5a4346a1ba64814bc05854a1577ca6a3672005 8044B
Tag: v12-final-fully-fledged-a4c1a228
Commit: 89f5f5d
Status: FINAL FULLY FLEDGED LAST BUILD

## What is POND?
Smallest kernel that uplifts Unix. Counter owned by kernel not chain.json.

## Builds

- v11-uplift-fa6660b3 7364B first kernel-owned counter
- v11.1-stable-5523b681 7572B offset 7520 warning-free q64 fixed deterministic
- v12-final-a4c1a228 8044B offset 7984 NVM 0x7E00 fully fledged

## v12 Improvements

1. NVM at 0x7E00 magic PONDVRNU 504F4E4456524E55
   struct magic + last_head + last_hash[4] + crc
   last_head() tries NVM first then RAM
   did_seal() writes RAM 7984 and NVM 0x7E00
   survives reboot, nvm_writes counter

2. Chain hash anti-replay
   can_seal checks new == last+1 and hash != NULL and hash != prev hash

3. Linker fix
   linker_256k.ld includes .pond_journal at 0x101f30 f40a0000 = 2804

4. Kernel main v12
   HEAD from journal_last_head not wall_q64
   chain_hash[4] = d,m,seal,out
   attest includes nvm_writes

5. 128K img
   MBR 55 AA at 510
   label at 0x200 POND v12 FINAL
   kernel at 0x1000
   NVM at 0x7E00 magic + head

## Build Proof

clang i686-elf Os flto ff-sections frandom-seed=b8e6709e979518ba
ld.lld linker_256k.ld gc-sections lto-O2
Size 8044 hash a4c1a2285f33c07a
Offset 7984 f40a = 2804
Deterministic 2x same hash
Warnings 0

## Attest HEAD 2806

Kernel a4c1a2285f33c07a mono same
sha256_chain 4a6b99691b2e83cec1d1c19023f9d31c72f2b075f3009a2dcfbaefa0b5763771
OP_RETURN POND0028064a6b99691b2e83ce
SOL Memo POND-HEAD-2806-CHAIN-4a6b99691b2e83ce-K-a4c1a2285f33c07a
ETH 0x508a063f23650f074df5452ec7b520cd7c367e7360a36992712b5ed940b0fa02
Health OK

## Files

pond-256k-v12-final-a4c1a228.bin 8044B final
pond-elf-256k-v12-final-a4c1a228.bin 14K
pond-128k-v12-final-2806.img 128K bootable NVM
pond-256k-v11.1-stable-5523b681.bin 7572B prev stable
chain.json live.json LIVE 2806

## Verify

sha256sum pond-256k.bin
python3 -c "import pathlib; raw=pathlib.Path('pond-256k.bin').read_bytes(); print(raw.find((2804).to_bytes(8,'little')))"
llvm-objdump -s -j .pond_journal pond-elf-256k.bin
python health.py
python attest.py

## Why Final

Kernel has own counter + NVM persistence + hash enforcement + self attest.
No more builds needed. Next would be real flash driver and full sha256 inside kernel - v13 hardware.

POND Embassy - kernel owns time not Unix.
