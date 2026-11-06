ENTRY(_start)
SECTIONS {
  . = 0x00100000;
  .text : { *(.text) }
  .rodata : { *(.rodata*) }
  .data : { *(.data) }
  .pond_journal : {
    KEEP(*(.pond_journal))
  }
  .bss : { *(.bss) *(COMMON) }
  /DISCARD/ : { *(.eh_frame) *(.comment) }
}
ASSERT(. <= 0x00108000, "POND-32K OVERFLOW: binary exceeds 32768 bytes")
