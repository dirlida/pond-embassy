typedef unsigned long long u64; typedef unsigned int u32;
u64 q64_mul_c(u64 a, u64 b){
  u64 a_lo = (u32)a; u64 a_hi = a>>32;
  u64 b_lo = (u32)b; u64 b_hi = b>>32;
  u64 lo_lo = a_lo * b_lo;
  u64 hi_lo = a_hi * b_lo;
  u64 lo_hi = a_lo * b_hi;
  // fixed: parentheses around + before <<
  u64 mid = hi_lo + lo_hi;
  return lo_lo + ((mid & 0xFFFFFFFFULL)<<32);
}
