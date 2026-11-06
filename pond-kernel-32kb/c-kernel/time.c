typedef unsigned long long u64;
extern u64 div64_c(u64,u64); extern u64 mod64_c(u64,u64);
int is_leap_c(int y){ return (y%4==0 && y%100!=0) || (y%400==0); }
int days_in_month_c(int y,int m){ static const unsigned char dm[12]={31,28,31,30,31,30,31,31,30,31,30,31}; int d=dm[m-1]; if(m==2&&is_leap_c(y)) d=29; return d; }
u64 wall_from_ymd_c(int y,int m,int d,int hh,int mm,int ss){
  u64 days=0; for(int yr=1970;yr<y;yr++) days+=365+is_leap_c(yr);
  for(int mo=1;mo<m;mo++) days+=days_in_month_c(y,mo);
  days+=d-1; u64 sec=days*86400ULL + hh*3600ULL+mm*60ULL+ss; return sec<<32;
}
void ymd_from_wall_c(u64 wall_q64,int *y,int *m,int *d,int *hh,int *mm,int *ss){
  u64 sec=wall_q64>>32; u64 days=div64_c(sec,86400ULL); u64 tod=mod64_c(sec,86400ULL);
  *hh=div64_c(tod,3600ULL); tod=mod64_c(tod,3600ULL); *mm=div64_c(tod,60ULL); *ss=mod64_c(tod,60ULL);
  int yr=1970; while(1){ u64 dy=365+is_leap_c(yr); if(days>=dy){days-=dy; yr++;} else break; } *y=yr;
  int mo=1; while(1){ int dim=days_in_month_c(yr,mo); if(days>= (u64)dim){days-=dim; mo++;} else break; } *m=mo; *d=(int)days+1;
}
u64 wall_add_sec_c(u64 w, int delta){ return w + ((u64)delta<<32); }
