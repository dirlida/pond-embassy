typedef unsigned long long u64; typedef long long s64;
u64 div64_c(u64 a, u64 b){ if(b==0) return 0; u64 q=0; for(int i=63;i>=0;i--){ if((a>>i)>=b){ a-=b<<i; q|=(1ULL<<i);} } return q; }
u64 mod64_c(u64 a, u64 b){ if(b==0) return a; for(int i=63;i>=0;i--){ if((a>>i)>=b) a-=b<<i; } return a; }
s64 divs64_c(s64 a, s64 b){ if(b==0) return 0; int neg=(a<0)^(b<0); u64 ua=a<0?-(u64)a:(u64)a; u64 ub=b<0?-(u64)b:(u64)b; u64 q=div64_c(ua,ub); return neg?-(s64)q:(s64)q; }
s64 mods64_c(s64 a, s64 b){ if(b==0) return a; u64 ua=a<0?-(u64)a:(u64)a; u64 ub=b<0?-(u64)b:(u64)b; u64 r=mod64_c(ua,ub); return a<0?-(s64)r:(s64)r; }
// libgcc shims for clang i686
u64 __udivdi3(u64 a, u64 b){ return div64_c(a,b); }
u64 __umoddi3(u64 a, u64 b){ return mod64_c(a,b); }
s64 __divdi3(s64 a, s64 b){ return divs64_c(a,b); }
s64 __moddi3(s64 a, s64 b){ return mods64_c(a,b); }
u64 __ashldi3(u64 a, int s){ return a<<s; }
u64 __ashrdi3(u64 a, int s){ return a>>s; }
u64 __lshrdi3(u64 a, int s){ return a>>s; }
