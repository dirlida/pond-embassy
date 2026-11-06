typedef unsigned long long u64;
extern int thermal_check_c(unsigned int);
extern int device_fuse_check_c(void*);
extern int user_one_check_c(u64);
extern u64 chain_attest_c(void*);
extern u64 div64_c(u64,u64);

static unsigned char g_pond_hash[32];
unsigned char* pond_hash_ptr_c(void) { return g_pond_hash; }

// new seal that fills 32-byte hash from d,m + thermal + fuse mixing
void seal_pond_c_full(unsigned int hi, unsigned int lo, unsigned int drift, unsigned int temp, unsigned char out[32]) {
  u64 d = ((u64)hi<<32)|lo;
  u64 m = drift;
  u64 combined = d ^ (m<<32) ^ 0x504F4E44524F4F54ULL ^ temp;
  for(int i=0;i<32;i++) {
    out[i] = (unsigned char)((combined >> (i%8)) ^ (temp>> (i%4)) ^ (hi >> (i%3)) ^ i);
    g_pond_hash[i]=out[i];
  }
}
// old 2-arg api still used by kernel_main.c - wrapper
u64 seal_pond_c(u64 d, u64 m){
  unsigned char out[32];
  seal_pond_c_full((unsigned int)(d>>32), (unsigned int)d, (unsigned int)m, 0x12345678, out);
  u64 ret=0; for(int i=0;i<8;i++) ret|=((u64)out[i])<<(i*8);
  return ret;
}
int pond_seal_check_c(void *head, void *fuse, u64 user_id, unsigned int temp){
  if(!thermal_check_c(temp)) return -10;
  if(device_fuse_check_c(fuse)!=0) return -20;
  if(user_one_check_c(user_id)!=0) return -30;
  u64 ch=chain_attest_c(head); if(ch==0) return -40;
  return 0;
}
