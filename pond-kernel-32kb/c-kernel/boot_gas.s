# 1 "boot_gas.S"
# 1 "<built-in>" 1
# 1 "<built-in>" 3
# 426 "<built-in>" 3
# 1 "<command line>" 1
# 1 "<built-in>" 2
# 1 "boot_gas.S" 2
.code32
.section .text
.global _start
_start:
  cli
  cld
  xor %eax,%eax
  mov %eax,%ds
  mov %eax,%es
  mov %eax,%ss
  mov $0x00180000,%esp
  call kernel_main
1:
  hlt
  jmp 1b
.global kernel_main_c
kernel_main_c:
  jmp kernel_main
