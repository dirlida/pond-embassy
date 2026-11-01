ENTRY(_start)
SECTIONS {
  . = 0x00100000;
  .text : { *(.text) }
  .rodata : { *(.rodata*) }
  .data : { *(.data) }
  .pond_journal : { *(.pond_journal) }
  .bss : { *(.bss) *(COMMON) }
  /DISCARD/ : { *(.eh_frame) *(.comment) }
}
