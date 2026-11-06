// journal.c - POND v13 RTC gap-fill - PATCH 1+2 FULL REWRITE
// Based on v12 FINAL, + RTC in NVM + allow gap jump
typedef unsigned long long u64; typedef unsigned int u32;
static u32 crc32_table[256]; static int crc_init=0;
void crc32_init_c(void){ if(crc_init) return; for(int i=0;i<256;i++){ u32 c=i; for(int j=0;j<8;j++) c=c&1?0xEDB88320U^(c>>1):c>>1; crc32_table[i]=c; } crc_init=1; }
u32 crc32_c(unsigned char *buf,int len){ crc32_init_c(); u32 crc=0xFFFFFFFFU; for(int i=0;i<len;i++) crc=crc32_table[(crc^buf[i])&0xFF]^(crc>>8); return crc^0xFFFFFFFFU; }

struct pond_head{ u64 magic; u64 device_id; u64 wall_q64; u64 raw_q64; u64 drift_q64; u64 sun_q32; struct{ long long lat_q32; long long lon_q32; } loc; unsigned int thermal; unsigned int boot_count; u64 prev_hash; unsigned int crc; u64 user_id; u64 chain_hash; } __attribute__((packed));
int journal_write_c(struct pond_head *dst, struct pond_head *src){ crc32_init_c(); for(int i=0;i<sizeof(*src);i++) ((unsigned char*)dst)[i]=((unsigned char*)src)[i]; u32 c=crc32_c((unsigned char*)dst, sizeof(*dst)-16); dst->crc=c; return 0; }
int journal_verify_c(struct pond_head *h){ u32 saved=h->crc; u32 calc=crc32_c((unsigned char*)h, sizeof(*h)-16); return saved==calc; }

// v12 FINAL: fully fledged kernel-owned counter with NVM emulation + chain hash
// v13: + last_rtc_q64 + gap_total_ticks in NVM
#define POND_NVM_MAGIC 0x504F4E4456524E55ULL // "PONDVRNU"
#define POND_NVM_ADDR ((volatile unsigned char*)0x00007E00)

struct pond_nvm {
  u64 magic;
  u64 last_head;
  u64 last_hash[4];
  u64 last_rtc_q64; // v13 NEW: last RTC wall in Q64, from CMOS RTC
  u64 gap_total_ticks; // v13 NEW: total ticks added by gap-fill, for audit
  u32 crc;
} __attribute__((packed));

__attribute__((used, section(".pond_journal")))
u64 last_sealed_head = 2804; // bumped to current LIVE

__attribute__((used, section(".pond_journal")))
u64 last_chain_hash[4] = {0};

__attribute__((used, section(".pond_journal")))
u64 nvm_write_count = 0;

// v13: keep last RTC in RAM mirror so we don't lose it on seal
__attribute__((used, section(".pond_journal")))
u64 last_rtc_mirror = 0;

__attribute__((used, section(".pond_journal")))
u64 gap_total_mirror = 0;

// try read NVM at 0x7E00, return 1 if valid
static int nvm_read(u64 *head, u64 *hash){
  struct pond_nvm *n = (struct pond_nvm*)POND_NVM_ADDR;
  if(n->magic != POND_NVM_MAGIC) return 0;
  u32 saved=n->crc;
  u32 calc=crc32_c((unsigned char*)n, sizeof(*n)-4);
  if(saved != calc) return 0;
  *head = n->last_head;
  for(int i=0;i<4;i++) hash[i]=n->last_hash[i];
  // v13: also restore RTC mirrors
  last_rtc_mirror = n->last_rtc_q64;
  gap_total_mirror = n->gap_total_ticks;
  return 1;
}

static void nvm_write(u64 head, u64 *hash){
  struct pond_nvm *n = (struct pond_nvm*)POND_NVM_ADDR;
  // in QEMU/real hw this would be flash write; here we just write RAM at 0x7E00
  // which survives if memory not cleared (emulates NVM)
  struct pond_nvm tmp;
  tmp.magic = POND_NVM_MAGIC;
  tmp.last_head = head;
  for(int i=0;i<4;i++) tmp.last_hash[i]=hash[i];
  // v13: PRESERVE RTC + gap total, don't wipe on seal
  tmp.last_rtc_q64 = last_rtc_mirror;
  tmp.gap_total_ticks = gap_total_mirror;
  tmp.crc = crc32_c((unsigned char*)&tmp, sizeof(tmp)-4);
  // write
  for(int i=0;i<sizeof(tmp);i++) ((volatile unsigned char*)n)[i]=((unsigned char*)&tmp)[i];
  nvm_write_count++;
}

u64 journal_last_head(void){
  u64 h; u64 hh[4];
  if(nvm_read(&h, hh)){
    last_sealed_head = h;
    for(int i=0;i<4;i++) last_chain_hash[i]=hh[i];
    return h;
  }
  return last_sealed_head;
}

// v13 PATCH 1: RTC helpers
u64 journal_last_rtc(void){
  // try to load from NVM first, to sync mirror
  u64 h; u64 hh[4];
  if(nvm_read(&h, hh)){
    // nvm_read already set last_rtc_mirror
    return last_rtc_mirror;
  }
  return last_rtc_mirror;
}

void journal_save_rtc(u64 rtc_q64){
  last_rtc_mirror = rtc_q64;
  // persist immediately, keep head/hash same
  u64 h = journal_last_head();
  u64 hh[4]; for(int i=0;i<4;i++) hh[i]=last_chain_hash[i];
  struct pond_nvm *n = (struct pond_nvm*)POND_NVM_ADDR;
  struct pond_nvm tmp;
  tmp.magic = POND_NVM_MAGIC;
  tmp.last_head = h;
  for(int i=0;i<4;i++) tmp.last_hash[i]=hh[i];
  tmp.last_rtc_q64 = rtc_q64;
  tmp.gap_total_ticks = gap_total_mirror;
  tmp.crc = crc32_c((unsigned char*)&tmp, sizeof(tmp)-4);
  for(int i=0;i<sizeof(tmp);i++) ((volatile unsigned char*)n)[i]=((unsigned char*)&tmp)[i];
  nvm_write_count++;
}

// v13: called by rtc_gap.c to record gap for audit
void journal_add_gap_ticks(u64 gap_ticks){
  gap_total_mirror += gap_ticks;
  // persist via nvm_write with current head/hash
  u64 h = journal_last_head();
  u64 hh[4]; for(int i=0;i<4;i++) hh[i]=last_chain_hash[i];
  nvm_write(h, hh);
}

u64 journal_gap_total(void){
  return gap_total_mirror;
}

// v13 PATCH 2: allow gap jump
int journal_can_seal(u64 new_head, u64* h){
  u64 cur = journal_last_head();
  // v13 rule: allow +1 normal OR gap jump (new_head > cur+1)
  // gap jump is only allowed when caller has proven RTC gap > 2 sec
  // we allow it here, kernel_main proves it in rtc_gap_fill_c
  if(new_head < cur + 1) return 0;
  if(h==0) return 0;
  // if we have stored hash, require new hash != old (prevent replay)
  if(last_chain_hash[0]!=0 && h[0]==last_chain_hash[0] && h[1]==last_chain_hash[1]) return 0;
  return 1;
}

void journal_did_seal(u64 new_head, u64* h){
  last_sealed_head=new_head;
  for(int i=0;i<4;i++) last_chain_hash[i]=h[i];
  nvm_write(new_head, h);
}

// v12 new API for Python to verify chain
int journal_verify_chain_hash(u64 *expected){
  if(expected==0) return 0;
  for(int i=0;i<4;i++) if(expected[i]!=last_chain_hash[i]) return 0;
  return 1;
}
u64 journal_nvm_writes(void){ return nvm_write_count; }
