#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#define CHAIN "legacy/chain.json"
#define HEAD_ID "a4c1a2285f33c07a"
#define INTERVAL 600
int get_last_live(){FILE*f=fopen(CHAIN,"rb");if(!f)return 2821;fseek(f,0,SEEK_END);long n=ftell(f);fseek(f,0,SEEK_SET);if(n<=0){fclose(f);return 2821;}char*b=malloc(n+1);fread(b,1,n,f);b[n]=0;fclose(f);int last=2821;char*p=b;while((p=strstr(p,"\"LIVE\":"))!=NULL){sscanf(p,"\"LIVE\":%d",&last);p+=7;}free(b);return last;}
void write_entry(int live){time_t now=time(NULL);struct tm* tm=gmtime(&now);char ts[32];strftime(ts,sizeof(ts),"%Y-%m-%dT%H:%M:%S+00:00",tm);FILE*f=fopen("/sys/class/thermal/thermal_zone0/temp","r");float tc=38.2;if(f){int t;if(fscanf(f,"%d",&t)==1)tc=t/1000.0;fclose(f);}FILE* out=fopen(CHAIN,"a");fprintf(out,"{\"HEAD\":\"%s\",\"LIVE\":%d,\"COUNT\":%d,\"TS\":\"%s\",\"TEMP\":\"%.1fC\",\"DRIFT\":0.05,\"INTERVAL\":600}\n",HEAD_ID,live,live,ts,tc);fclose(out);FILE* lg=fopen("pond.log","a");if(lg){fprintf(lg,"%s LIVE %d (10m)\n",ts,live);fclose(lg);}}
int main(int argc,char** argv){int bg=1;if(argc>1&&strcmp(argv[1],"--fg")==0)bg=0;if(bg){if(fork()!=0)return 0;setsid();if(fork()!=0)return 0;fclose(stdin);fclose(stdout);fclose(stderr);}system("termux-wake-lock 2>/dev/null");int live=get_last_live();while(1){live++;write_entry(live);sleep(INTERVAL);}return 0;}
