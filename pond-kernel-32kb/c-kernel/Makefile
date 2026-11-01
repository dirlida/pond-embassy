CC=clang
AS=clang
LD=ld.lld
CFLAGS=-target i686-elf -ffreestanding -nostdlib -fno-stack-protector -fno-builtin -O2 -frandom-seed=fbcbad2c5324f560
LDFLAGS=-T linker_32k.ld -nostdlib
OBJS=boot_gas.o kernel_main.o q32.o div64.o q64.o time.o five_clock_vote.o sun.o journal.o chain_attest.o sha256.o thermal.o device_fuse.o user_one.o seal.o
all: pond-32k.bin
	@ls -lh pond-32k.bin; wc -c pond-32k.bin
pond-elf.bin: $(OBJS)
	$(LD) $(LDFLAGS) -o $@ $^
pond-32k.bin: pond-elf.bin
	llvm-objcopy -O binary $< $@
boot_gas.o: boot_gas.s
	$(AS) --target=i686-elf -c $< -o $@
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@
clean:
	rm -f *.o *.bin pond-elf.bin
