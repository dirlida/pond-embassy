.code16
.global _start
_start:
  cli
  ljmp $0, $1f
1:  xor %ax, %ax
  mov %ax, %ds
  mov %ax, %ss
  mov $0x7c00, %sp
  call enable_a20
  lgdt gdt_desc
  mov %cr0, %eax
  or $1, %eax
  mov %eax, %cr0
  ljmp $0x08, $protected
.code32
protected:
  mov $0x10, %ax
  mov %ax, %ds
  mov %ax, %es
  mov %ax, %ss
  mov $0x7c00, %esp
  call kernel_main
.hlt:
  hlt
  jmp .hlt
enable_a20:
  in $0x92, %al
  or $2, %al
  out %al, $0x92
  ret
.align 4
gdt:
  .quad 0
  .quad 0x00cf9a000000ffff
  .quad 0x00cf92000000ffff
gdt_desc:
  .word gdt_desc - gdt - 1
  .long gdt
