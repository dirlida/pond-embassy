all: pond.bin pond-32kb.img

boot.o: boot_gas.s
	clang --target=i686-elf -m32 -c boot_gas.s -o boot.o

div64.o: div64.c
	clang --target=i686-elf -m32 -ffreestanding -fno-builtin -c div64.c -o div64.o

kernel.o: kernel.c
	clang --target=i686-elf -m32 -ffreestanding -fno-builtin -c kernel.c -o kernel.o

pond.bin: boot.o div64.o kernel.o linker.ld fix.py
	ld.lld -m elf_i386 -T linker.ld boot.o div64.o kernel.o -o pond.elf
	llvm-objcopy -O binary pond.elf pond.bin
	python3 fix.py
	ls -lh pond.bin pond.elf

pond-32kb.img: pond.bin
	dd if=/dev/zero of=pond-32kb.img bs=1024 count=32 2>/dev/null
	dd if=pond.bin of=pond-32kb.img conv=notrunc 2>/dev/null
	ls -lh pond-32kb.img

clean:
	rm -f *.o *.elf *.bin *.img
