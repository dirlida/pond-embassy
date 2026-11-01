# POND Embassy v12 Final - 8044B fully fledged

HEAD 2806 LIVE 2806 Kernel a4c1a2285f33c07a

Final kernel 8044B at offset 7984 counter 2804 NVM 0x7E00.

## Quick verify
sha256sum pond-kernel-32kb/final-bins/pond-256k-v12-final-a4c1a228.bin
# a4c1a2285f33c07a679989f4ce5a4346a1ba64814bc05854a1577ca6a3672005

python health.py # OK
python attest.py # HEAD 2806 4a6b9969

## Zenodo upload list
- pond-256k-v12-final-a4c1a228.bin 8044B a4c1a2285f33c07a
- pond-elf-256k-v12-final-a4c1a228.bin 13652B
- pond-128k-v12-final-2806.img 131072B
- pond-256k-v11.1-stable-5523b681.bin 7572B 5523b681 prev stable
- pond-elf-256k-v11.1-stable-5523b681.bin
- RELEASE_NOTES_v12-final.md
- chain.json live.json

Tag: v12.0.0 + v12-final-fully-fledged-a4c1a228

Done done - embassy kernel final.
