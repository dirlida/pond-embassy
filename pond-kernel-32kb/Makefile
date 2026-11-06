# POND v13 - top-level offline wrapper
all:
	$(MAKE) -C c-kernel
clean:
	$(MAKE) -C c-kernel clean
verify:
	cd c-kernel && python3 verify_v13.py
	python3 pond_daemon.py
	cd c-kernel && sha256sum -c pond-32k-v13.sha256
qemu:
	qemu-system-i386 -kernel c-kernel/pond-32k.bin -nographic
