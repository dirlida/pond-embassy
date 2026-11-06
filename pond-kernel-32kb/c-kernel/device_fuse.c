typedef unsigned long long u64;
static const u64 FUSE_MAGIC=0x504F4E4446555345ULL;
struct fuse{ u64 magic; u64 id; u64 key; u64 seal; };
int device_fuse_check_c(struct fuse *f){ if(!f) return -1; if(f->magic!=FUSE_MAGIC) return -2; if((f->id ^ f->key)!=f->seal) return -3; return 0; }
u64 device_fuse_id_c(struct fuse *f){ return f?f->id:0; }
