typedef unsigned long long u64; typedef long long s64;
struct clock_vote{ u64 raw_q64; u64 wall_q64; u64 drift_q32; };
extern u64 div64_c(u64,u64);
void sort5_u64(u64 *a){ for(int i=0;i<5;i++) for(int j=i+1;j<5;j++) if(a[j]<a[i]){u64 t=a[i]; a[i]=a[j]; a[j]=t;} }
struct clock_vote five_clock_vote_c(u64 tsc){
  u64 samples[5]; for(int i=0;i<5;i++){ samples[i]=tsc + i*1000ULL + (i*0x9E3779B97F4A7C15ULL>>32); for(volatile int k=0;k<100;k++); }
  sort5_u64(samples); u64 median=samples[2]; u64 sum=0; for(int i=0;i<5;i++) sum+=samples[i];
  u64 avg=div64_c(sum,5ULL); s64 drift=(s64)(median-avg); if(drift<0) drift=-drift;
  struct clock_vote v; v.raw_q64=tsc; v.wall_q64=median; v.drift_q32=((u64)drift & 0xFFFFFFFFULL); return v;
}
