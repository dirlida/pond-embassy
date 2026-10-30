POND v5.1 PHYSICAL + EMBASSY v1
PHONE (Termux aarch64, lo, cntvct_el0):
  embassy -> No HW stamp -> UNCERT 6000000 ns = Google TrueTime 6ms
  pond.bin -> boots QEMU 55aa, MATH Q32 real

IBM (x86_64, eth0 i210, rdtsc + HPET FED00000h):
  embassy + linuxptp -> HW stamp ENABLED -> UNCERT 100 ns beats Google 60k x
  pond.bin -> boots bare metal <50us

RAW NEVER LAGS (offline TSC/cntvct)
WALL MAY LAG (PTP 100ns HW vs NTP 3ms vs Google 6ms SW)
