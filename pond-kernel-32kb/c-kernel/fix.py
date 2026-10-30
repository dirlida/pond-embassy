with open("pond.bin","r+b") as f:
    d=f.read()
    if len(d)<512:
        f.write(b'\x00'*(512-len(d)))
    f.seek(510)
    f.write(bytes([0x55,0xAA]))
