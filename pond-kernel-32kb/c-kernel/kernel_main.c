typedef unsigned long long u64; typedef long long s64;
struct location_q32{ s64 lat_q32; s64 lon_q32; };
struct clock_vote{ u64 raw_q64; u64 wall_q64; u64 drift_q32; };
extern unsigned int thermal_read_c(void);
extern struct clock_vote five_clock_vote_c(u64);
extern u64 sun_angle_q32_c(u64, struct location_q32);
extern void sha256_chain(unsigned char *in,int len,u64 *out);
extern u64 div64_c(u64,u64); extern u64 mod64_c(u64,u64);
extern s64 q32_mul_c(s64,s64); extern s64 q32_sin_q32_c(s64); extern u64 q64_mul_c(u64,u64);
extern int journal_write_c(void*,void*); extern int journal_verify_c(void*);
extern u64 chain_attest_c(void*); extern u64 seal_pond_c(u64,u64);
extern int device_fuse_check_c(void*); extern int user_one_check_c(u64);
extern unsigned int crc32_c(unsigned char*,int);
extern u64 journal_last_head(void);
extern int journal_can_seal(u64,u64*);
extern void journal_did_seal(u64,u64*);
extern u64 journal_nvm_writes(void);
extern u64 rtc_gap_fill_c(u64*,u64*);
extern u64 journal_gap_total(void);

void kernel_main(void){
  volatile unsigned int t=thermal_read_c();
  struct clock_vote v=five_clock_vote_c(1000000000ULL);
  struct location_q32 loc={0x12345678,0x87654321};
  volatile u64 s=sun_angle_q32_c(v.wall_q64, loc);
  u64 out[2]; unsigned char msg[]="pond-kernel-32k-pond-kernel-32k";
  sha256_chain(msg,32,out);
  s64 q=q32_mul_c((s64)s,(s64)loc.lat_q32);
  s64 qs=q32_sin_q32_c(q);
  u64 qm=q64_mul_c(s,(u64)qs);
  unsigned char buf[128]; for(int i=0;i<128;i++) buf[i]=i;
  unsigned int crc=crc32_c(buf,128);
  u64 d=div64_c(qm,crc?crc:1); u64 m=mod64_c(qm,crc?crc:1);
  u64 seal=seal_pond_c(d,m);
  int u=user_one_check_c(seal);
  // v13 RTC GAP-FILL: check if we were OFF, before sealing
  u64 gap_ticks=0, gap_sec=0;
  u64 last_head = journal_last_head();
  u64 gap_head = rtc_gap_fill_c(&gap_ticks, &gap_sec);
  u64 new_head = (gap_sec > 2) ? gap_head : (last_head + 1);
  u64 chain_hash[4] = {d,m,seal,out[0]};
  int can = journal_can_seal(new_head, chain_hash);
  u64 nvm_w = 0;
  if(can){
    journal_did_seal(new_head, chain_hash);
    nvm_w = journal_nvm_writes();
  }
  struct { u64 head; u64 seal; unsigned char ph[32]; u64 nvm_writes; u64 gap_ticks; u64 gap_sec; u64 gap_total; } attest;
  attest.head = new_head;
  attest.seal = seal;
  for(int i=0;i<32;i++) attest.ph[i]=((unsigned char*)chain_hash)[i];
  attest.nvm_writes = nvm_w;
  attest.gap_ticks = gap_ticks;
  attest.gap_sec = gap_sec;
  attest.gap_total = journal_gap_total();
  journal_write_c(&attest, (void*)sizeof(attest));
  chain_attest_c(&attest);
  (void)t;(void)s;(void)out;(void)u;(void)d;(void)can;
  while(1){ // portable halt
#if defined(__x86_64__) || defined(__i386__)
  __asm__ volatile("hlt");
#else
  __asm__ volatile("wfi");
#endif
}
}
