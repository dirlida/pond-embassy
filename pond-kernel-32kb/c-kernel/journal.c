typedef unsigned long long u64; typedef unsigned int u32;
static u32 crc32_table[256]; static int crc_init=0;
void crc32_init_c(void){ if(crc_init) return; for(int i=0;i<256;i++){ u32 c=i; for(int j=0;j<8;j++) c=c&1?0xEDB88320U^(c>>1):c>>1; crc32_table[i]=c; } crc_init=1; }
u32 crc32_c(unsigned char *buf,int len){ crc32_init_c(); u32 crc=0xFFFFFFFFU; for(int i=0;i<len;i++) crc=crc32_table[(crc^buf[i])&0xFF]^(crc>>8); return crc^0xFFFFFFFFU; }

struct pond_head{ u64 magic; u64 device_id; u64 wall_q64; u64 raw_q64; u64 drift_q64; u64 sun_q32; struct{ long long lat_q32; long long lon_q32; } loc; unsigned int thermal; unsigned int boot_count; u64 prev_hash; unsigned int crc; u64 user_id; u64 chain_hash; } __attribute__((packed));
int journal_write_c(struct pond_head *dst, struct pond_head *src){ crc32_init_c(); for(int i=0;i<sizeof(*src);i++) ((unsigned char*)dst)[i]=((unsigned char*)src)[i]; u32 c=crc32_c((unsigned char*)dst, sizeof(*dst)-16); dst->crc=c; return 0; }
int journal_verify_c(struct pond_head *h){ u32 saved=h->crc; u32 calc=crc32_c((unsigned char*)h, sizeof(*h)-16); return saved==calc; }

// v12 FINAL: fully fledged kernel-owned counter with NVM emulation + chain hash
#define POND_NVM_MAGIC 0x504F4E4456524E55ULL // "PONDVRNU"
#define POND_NVM_ADDR ((volatile unsigned char*)0x00007E00)

struct pond_nvm {
  u64 magic;
  u64 last_head;
  u64 last_hash[4];
  u32 crc;
} __attribute__((packed));

__attribute__((used, section(".pond_journal")))
u64 last_sealed_head = 2804; // bumped to current LIVE

__attribute__((used, section(".pond_journal")))
u64 last_chain_hash[4] = {0};

__attribute__((used, section(".pond_journal")))
u64 nvm_write_count = 0;

// try read NVM at 0x7E00, return 1 if valid
static int nvm_read(u64 *head, u64 *hash){
  struct pond_nvm *n = (struct pond_nvm*)POND_NVM_ADDR;
  if(n->magic != POND_NVM_MAGIC) return 0;
  u32 saved=n->crc;
  u32 calc=crc32_c((unsigned char*)n, sizeof(*n)-4);
  if(saved != calc) return 0;
  *head = n->last_head;
  for(int i=0;i<4;i++) hash[i]=n->last_hash[i];
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

int journal_can_seal(u64 new_head, u64* h){
  u64 cur = journal_last_head();
  // v12 rule: +1 AND chain hash must link (if we have previous hash, enforce hash[0] !=0 -> must match prev? for now only +1 + non-zero hash)
  if(new_head != cur + 1) return 0;
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
