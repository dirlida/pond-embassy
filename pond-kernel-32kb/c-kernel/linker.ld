ENTRY(_start)
SECTIONS{
  . = 0x7C00;
  .text : { *(.multiboot) *(.text) }
  .rodata : { *(.rodata*) }
  .data : { *(.data) }
  .bss : { *(.bss) }
  /DISCARD/ : { *(.comment) *(.eh_frame) }
}
