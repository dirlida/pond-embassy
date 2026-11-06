unsigned int thermal_table_c[64]={16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60,62,64,66,68,70,72,74,76,78,80,82,84,86,88,90,92,94,96,98,100,102,104,106,108,110,112,114,116,118,120,122,124,126,128,130,132,134,136,138,140,142};
int thermal_check_c(unsigned int t){return t<0x90;}
unsigned int thermal_read_c(void){unsigned int s=0;for(int i=0;i<64;i++)s+=thermal_table_c[i];return s&0xFF;}
