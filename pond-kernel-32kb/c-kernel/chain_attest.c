typedef unsigned long long u64; typedef unsigned int u32;
extern u32 crc32_c(unsigned char*,int);
extern void sha256_chain(unsigned char*,int,u64*);
struct pond_head{ u64 magic; u64 device_id; u64 wall_q64; u64 raw_q64; u64 drift_q64; u64 sun_q32; struct{ long long lat_q32; long long lon_q32; } loc; unsigned int thermal; unsigned int boot_count; u64 prev_hash; unsigned int crc; u64 user_id; u64 chain_hash; } __attribute__((packed));
u64 chain_attest_c(struct pond_head *h){
  if(!h) return 0;
  u32 crc=crc32_c((unsigned char*)h, sizeof(*h)-16);
  if(crc!=h->crc) return 0;
  u64 out[2]; sha256_chain((unsigned char*)h, 64, out);
  u64 chain=out[0] ^ out[1] ^ h->prev_hash ^ h->device_id;
  h->chain_hash=chain; return chain;
}
