typedef unsigned long long u64;
extern u64 journal_last_head(void);
extern u64 journal_last_rtc(void);
extern void journal_save_rtc(u64);
extern void journal_add_gap_ticks(u64);
extern u64 wall_from_ymd_c(int,int,int,int,int,int);

// Portable CMOS read: real on x86, stub on ARM (for local test compile)
static unsigned char cmos_read(unsigned char reg){
#if defined(__x86_64__) || defined(__i386__)
  unsigned char out;
  __asm__ volatile("outb %0, $0x70" :: "a"(reg));
  __asm__ volatile("inb $0x71, %0" : "=a"(out));
  return out;
#else
  // ARM / phone: no CMOS ports. Return 0, caller falls back to wall vote.
  // On real x86 kernel build, the #if above is used.
  (void)reg;
  return 0;
#endif
}
static unsigned char bcd_to_bin(unsigned char v){
  return (v & 0x0F) + ((v>>4)*10);
}
u64 rtc_read_q64_c(void){
#if defined(__x86_64__) || defined(__i386__)
  while(cmos_read(0x0A) & 0x80);
  unsigned char sec = cmos_read(0x00);
  unsigned char min = cmos_read(0x02);
  unsigned char hour = cmos_read(0x04);
  unsigned char day = cmos_read(0x07);
  unsigned char month = cmos_read(0x08);
  unsigned char year = cmos_read(0x09);
  sec = bcd_to_bin(sec); min = bcd_to_bin(min); hour = bcd_to_bin(hour);
  day = bcd_to_bin(day); month = bcd_to_bin(month); year = bcd_to_bin(year);
  int full_year = 2000 + year;
  return wall_from_ymd_c(full_year, month, day, hour, min, sec);
#else
  // ARM test stub: no real RTC here, return 0 so gap-fill safely does +1
  // Real RTC on phone will be added via Android RTC driver later, not CMOS
  return 0;
#endif
}

u64 rtc_gap_fill_c(u64 *out_gap_ticks, u64 *out_gap_sec){
  u64 last_head = journal_last_head();
  u64 last_rtc = journal_last_rtc();
  u64 rtc_now = rtc_read_q64_c();
  if(last_rtc == 0 || rtc_now == 0){
    if(rtc_now != 0) journal_save_rtc(rtc_now);
    *out_gap_ticks = 0; *out_gap_sec = 0;
    return last_head;
  }
  u64 gap_q64 = (rtc_now > last_rtc) ? (rtc_now - last_rtc) : 0;
  u64 gap_sec = gap_q64 >> 32;
  if(gap_sec <= 2){
    journal_save_rtc(rtc_now);
    *out_gap_ticks = 0; *out_gap_sec = 0;
    return last_head;
  }
  u64 gap_ticks = gap_sec;
  *out_gap_ticks = gap_ticks; *out_gap_sec = gap_sec;
  journal_add_gap_ticks(gap_ticks);
  journal_save_rtc(rtc_now);
  return last_head + gap_ticks;
}
