typedef unsigned long long u64; typedef unsigned int u32;
static u32 crc32_table[256]; static int crc_init=0;
void crc32_init_c(void){ if(crc_init) return; for(int i=0;i<256;i++){ u32 c=i; for(int j=0;j<8;j++) c=c&1?0xEDB88320U^(c>>1):c>>1; crc32_table[i]=c; } crc_init=1; }
u32 crc32_c(unsigned char *buf,int len){ crc32_init_c(); u32 crc=0xFFFFFFFFU; for(int i=0;i<len;i++) crc=crc32_table[(crc^buf[i])&0xFF]^(crc>>8); return crc^0xFFFFFFFFU; }
struct pond_head{ u64 magic; u64 device_id; u64 wall_q64; u64 raw_q64; u64 drift_q64; u64 sun_q32; struct{ long long lat_q32; long long lon_q32; } loc; unsigned int thermal; unsigned int boot_count; u64 prev_hash; unsigned int crc; u64 user_id; u64 chain_hash; } __attribute__((packed));
int journal_write_c(struct pond_head *dst, struct pond_head *src){ crc32_init_c(); for(int i=0;i<sizeof(*src);i++) ((unsigned char*)dst)[i]=((unsigned char*)src)[i]; u32 c=crc32_c((unsigned char*)dst, sizeof(*dst)-16); dst->crc=c; return 0; }
int journal_verify_c(struct pond_head *h){ u32 saved=h->crc; u32 calc=crc32_c((unsigned char*)h, sizeof(*h)-16); return saved==calc; }
// v11.1 uplift: counter in dedicated section, used, not GC'd
__attribute__((used, section(".pond_journal")))
u64 last_sealed_head = 2802;
__attribute__((used, section(".pond_journal")))
u64 last_chain_hash[4] = {0};
int journal_can_seal(u64 new_head, u64* h){ return new_head == last_sealed_head + 1; }
void journal_did_seal(u64 new_head, u64* h){ last_sealed_head=new_head; for(int i=0;i<4;i++) last_chain_hash[i]=h[i]; }
u64 journal_last_head(void){ return last_sealed_head; }
