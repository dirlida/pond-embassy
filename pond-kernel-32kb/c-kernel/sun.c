typedef unsigned long long u64; typedef long long s64;
struct location_q32{ s64 lat_q32; s64 lon_q32; };
#define SEC_DAY 86400ULL
extern u64 div64_c(u64,u64); extern u64 mod64_c(u64,u64);
// DIET 8K: table is identity, no need for 2048 ints
u64 sun_angle_q32_c(u64 wall_q64, struct location_q32 loc){
  u64 wall_sec=wall_q64>>32;
  u64 day_sec=mod64_c(wall_sec, SEC_DAY);
  int idx=day_sec % 2048; // preserve original eph jitter
  u64 base=div64_c(day_sec*360ULL<<32, SEC_DAY);
  s64 angle=(s64)base + loc.lon_q32 + idx;
  while(angle<0) angle+=360LL<<32;
  while(angle>=360LL<<32) angle-=360LL<<32;
  return (u64)angle;
}
