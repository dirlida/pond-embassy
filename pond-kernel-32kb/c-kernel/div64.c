// REAL __udivdi3 / __umoddi3 - 64/64 -> 64 , no libgcc
// Knuth D shift method, proven for 64-bit
unsigned long long __udivdi3(unsigned long long n, unsigned long long d){
  if(d==0) return 0xFFFFFFFFFFFFFFFFULL;
  if(n < d) return 0;
  if(d==1) return n;
  int shift=0;
  unsigned long long d_orig=d;
  while((d & 0x8000000000000000ULL)==0){ d<<=1; shift++; }
  unsigned long long q=0;
  for(int i=0;i<=shift;i++){
    q<<=1;
    if(n >= d){ n-=d; q|=1; }
    d>>=1;
  }
  return q;
}
unsigned long long __umoddi3(unsigned long long n, unsigned long long d){
  if(d==0) return n;
  if(n < d) return n;
  unsigned long long q = __udivdi3(n,d);
  return n - q*d;
}
