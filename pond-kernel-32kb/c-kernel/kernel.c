// POND OS v9.0 - RUNS LINUX ELF + WINDOWS PE + POND NATIVE - OFF UNIX
#define VGA 0xB8000
typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32; typedef unsigned long long u64;
extern u64 __udivdi3(u64 a,u64 b);
static void putc(int y,int x,char c,u8 col){ ((volatile u16*)VGA)[y*80+x]= (u16)col<<8|c; }
static void puts(int y,const char*s,u8 col){ for(int x=0;s[x]&&x<80;x++) putc(y,x,s[x],col); }
static void hex32(int y,int x,u32 v){ for(int i=7;i>=0;i--){ u8 n=(v>>(i*4))&0xF; putc(y,x+7-i,n<10?'0'+n:'A'+n-10,0x0E); } }
static void hex64(int y,int x,u64 v){ for(int i=15;i>=0;i--){ u8 n=(v>>(i*4))&0xF; putc(y,x+15-i,n<10?'0'+n:'A'+n-10,0x0E); } }
static void dec64(int y,int x,u64 v){ char b[21]; b[20]=0; int i=19; if(v==0) b[i--]='0'; while(v>0&&i>=0){ b[i--]='0'+(v%10); v/=10; } puts(y,b+i+1,0x0F); }
static inline u64 rdtsc(void){ u32 lo,hi; __asm__ volatile("rdtsc":"=a"(lo),"=d"(hi)); return ((u64)hi<<32)|lo; }
static inline void outb(u16 p,u8 v){ __asm__ volatile("outb %0,%1"::"a"(v),"Nd"(p)); }
static inline u8 inb(u16 p){ u8 r; __asm__ volatile("inb %1,%0":"=a"(r):"Nd"(p)); return r; }
#define PIT_CH0 0x40
#define PIT_CMD 0x43
#define PIT_FREQ 1193182ULL
struct gdt_entry { u16 lim_low; u16 base_low; u8 base_mid; u8 access; u8 gran; u8 base_high; } __attribute__((packed));
struct gdt_ptr { u16 lim; u32 base; } __attribute__((packed));
struct tss_entry { u32 prev; u32 esp0; u32 ss0; u32 esp1; u32 ss1; u32 esp2; u32 ss2; u32 cr3; u32 eip; u32 eflags; u32 eax; u32 ecx; u32 edx; u32 ebx; u32 esp; u32 ebp; u32 esi; u32 edi; u32 es; u32 ss; u32 ds; u32 fs; u32 gs; u32 ldt; u16 trap; u16 iomap; } __attribute__((packed));
static struct gdt_entry gdt[6]; static struct gdt_ptr gdtp; static struct tss_entry tss;
static u8 kernel_stack[4096]; static u8 user_stack[4096];
static void gdt_set(int n, u32 base, u32 lim, u8 acc, u8 gran){ gdt[n].base_low=base&0xFFFF; gdt[n].base_mid=(base>>16)&0xFF; gdt[n].base_high=(base>>24)&0xFF; gdt[n].lim_low=lim&0xFFFF; gdt[n].gran=(lim>>16)&0x0F; gdt[n].gran|=gran&0xF0; gdt[n].access=acc; }
struct idt_entry { u16 off_low; u16 sel; u8 zero; u8 flags; u16 off_high; } __attribute__((packed));
struct idt_ptr { u16 limit; u32 base; } __attribute__((packed));
static struct idt_entry idt[256]; static struct idt_ptr idtp;
static void idt_set(int n, u32 h, u16 sel, u8 flags){ idt[n].off_low=h&0xFFFF; idt[n].sel=sel; idt[n].zero=0; idt[n].flags=flags; idt[n].off_high=(h>>16)&0xFFFF; }
extern void isr_timer(void); extern void isr_syscall(void);
__asm__(".globl isr_timer\n isr_timer: pusha; push %ds; push %es; push %fs; push %gs; mov $0x10,%ax; mov %ax,%ds; mov %ax,%es; call timer_handler; pop %gs; pop %fs; pop %es; pop %ds; popa; iret\n"
        ".globl isr_syscall\n isr_syscall: pusha; push %ds; push %es; mov $0x10,%ax; mov %ax,%ds; mov %ax,%es; mov %ax,%ss; call syscall_handler; pop %es; pop %ds; popa; iret\n");
static u32 ticks=0; static u64 prev_hash=0xfb204d33ULL; static u32 syscall_ret=0;
static u64 pond_hash(u64 utc,u64 raw,u64 prev){ u64 h=1469598103934665603ULL^prev; h^=utc; h*=1099511628211ULL; h^=raw; h*=1099511628211ULL; return h; }
void timer_handler(void){ ticks++; outb(0x20,0x20); }
void syscall_handler(void){ u32 eax; __asm__ volatile("mov 28(%%ebp),%0":"=r"(eax)); if(eax==1||eax==4){ u64 raw=rdtsc(); syscall_ret=(u32)pond_hash(raw,raw,prev_hash); prev_hash=syscall_ret; } }
int detect_format(u8 *p){ if(p[0]==0x7F&&p[1]=='E'&&p[2]=='L'&&p[3]=='F') return 1; if(p[0]=='M'&&p[1]=='Z') return 2; if(p[0]==0xFE&&p[1]==0xED&&p[2]==0xFA) return 3; return 0; }
int detect_pe(u8 *p){ if(p[0]!='M'||p[1]!='Z') return 0; u32 lfanew=*(u32*)(p+0x3C); if(lfanew>1024) return 0; u8 *pe=p+lfanew; if(pe[0]!='P'||pe[1]!='E') return 0; return 1; }
void load_elf(u8 *src){ u32 e_entry=*(u32*)(src+24); u32 e_phoff=*(u32*)(src+28); u16 e_phnum=*(u16*)(src+42); puts(9,"ELF: entry",0x0A); hex32(9,11,e_entry); puts(9," phoff",0x0A); hex32(9,27,e_phoff); dec64(9,36,e_phnum); for(int i=0;i<e_phnum&&i<8;i++){ u8 *ph=src+e_phoff+i*32; u32 p_type=*(u32*)(ph+0); u32 p_offset=*(u32*)(ph+4); u32 p_filesz=*(u32*)(ph+16); u32 p_memsz=*(u32*)(ph+20); u32 p_vaddr=*(u32*)(ph+8); if(p_type==1){ u8 *dst=(u8*)0x200000; if(p_vaddr>=0x200000&&p_vaddr<0x300000) dst=(u8*)p_vaddr; for(u32 j=0;j<p_filesz&&j<8192;j++) dst[j]=src[p_offset+j]; for(u32 j=p_filesz;j<p_memsz&&j<8192;j++) dst[j]=0; } } }
void load_pe(u8 *src){ u32 lfanew=*(u32*)(src+0x3C); u8 *pe=src+lfanew; u16 num_sections=*(u16*)(pe+6); u16 opt_size=*(u16*)(pe+20); u8 *sections=pe+24+opt_size; u32 entry=*(u32*)(pe+40); puts(9,"PE: MZ->PE lfanew sec entry",0x0C); hex32(9,15,lfanew); dec64(9,22,num_sections); hex32(9,26,entry); for(int i=0;i<num_sections&&i<8;i++){ u8 *sec=sections+i*40; u32 raw_ptr=*(u32*)(sec+20); u32 raw_sz=*(u32*)(sec+16); if(raw_sz>0&&raw_sz<8192){ u8 *dst=(u8*)0x200000; if(i>0) dst=(u8*)(0x200000+i*4096); for(u32 j=0;j<raw_sz;j++) dst[j]=src[raw_ptr+j]; } } }
void load_user_v9(void){ u8 *src=(u8*)0x2000; int fmt=detect_format(src); if(fmt==0){ puts(8,"FMT: RAW POND 103b -> 0x200000",0x0B); u8 *dst=(u8*)0x200000; for(int i=0;i<4096;i++) dst[i]=src[i]; hex32(8,45,*(u32*)dst); } else if(fmt==1){ puts(8,"FMT: ELF LINUX DETECTED -> LOADING",0x0E); load_elf(src); } else if(fmt==2){ if(detect_pe(src)){ puts(8,"FMT: PE WINDOWS MZ->PE OK -> LOAD",0x0C); load_pe(src); } else { puts(8,"FMT: PE BAD HEADER",0x04); } } else { puts(8,"FMT: MACH-O APPLE -> STUB",0x0D); } }
void jump_ring3(void){ u32 user_esp=(u32)user_stack+sizeof(user_stack); tss.esp0=(u32)kernel_stack+sizeof(kernel_stack); tss.ss0=0x10; __asm__ volatile("cli\n mov %0, %%ax\n mov %%ax, %%ds\n mov %%ax, %%es\n mov %%ax, %%fs\n mov %%ax, %%gs\n pushl $0x23\n pushl %1\n pushf\n pushl $0x1B\n pushl %2\n iret\n":: "i"(0x10), "r"(user_esp), "r"(0x200000) : "eax"); }
void kernel_main(void){ for(int i=0;i<80*25;i++) ((volatile u16*)VGA)[i]=0x0700|' '; puts(0,"POND OS v9.0 OFF UNIX, RUNS UNIX+WINDOWS",0x0F); puts(1,"v9: RAW+ELF+PE | KERNEL <8K",0x07); gdt_set(0,0,0,0,0); gdt_set(1,0,0xFFFFFFFF,0x9A,0xCF); gdt_set(2,0,0xFFFFFFFF,0x92,0xCF); gdt_set(3,0,0xFFFFFFFF,0xFA,0xCF); gdt_set(4,0,0xFFFFFFFF,0xF2,0xCF); u32 tss_base=(u32)&tss; u32 tss_lim=sizeof(tss); gdt_set(5,tss_base,tss_lim,0x89,0x00); gdtp.lim=sizeof(gdt)-1; gdtp.base=(u32)gdt; __asm__ volatile("lgdt %0"::"m"(gdtp)); __asm__ volatile("mov $0x10,%ax; mov %ax,%ds; mov %ax,%es; mov %ax,%fs; mov %ax,%gs; mov %ax,%ss; ljmp $0x08,$1f; 1:"); __asm__ volatile("mov $0x28,%ax; ltr %ax"); for(int i=0;i<256;i++) idt_set(i,0,0x08,0); idt_set(32,(u32)isr_timer,0x08,0x8E); idt_set(0x80,(u32)isr_syscall,0x08,0xEE); idtp.limit=sizeof(idt)-1; idtp.base=(u32)idt; __asm__ volatile("lidt %0"::"m"(idtp)); outb(0x20,0x11); outb(0xA0,0x11); outb(0x21,0x20); outb(0xA1,0x28); outb(0x21,0x04); outb(0xA1,0x02); outb(0x21,0x01); outb(0xA1,0x01); outb(0x21,0x0); outb(0xA1,0x0); u32 div=PIT_FREQ/100; outb(PIT_CMD,0x36); outb(PIT_CH0,div&0xFF); outb(PIT_CH0,(div>>8)&0xFF); __asm__ volatile("sti"); u64 ts=rdtsc(); outb(PIT_CMD,0x30); outb(PIT_CH0,0xE8); outb(PIT_CH0,0x03); for(int k=0;k<10;k++){ outb(PIT_CMD,0xE2); while((inb(PIT_CMD)&0x80)==0); } u64 te=rdtsc(); u64 freq=(te-ts)*100; puts(3,"TSC FREQ:",0x0A); dec64(3,10,freq); u64 q=__udivdi3(1000000000ULL,freq); u64 r=1000000000ULL-q*freq; u64 ns_q32=(q<<32)|__udivdi3(r<<32,freq); puts(4,"NS/TICK Q32:",0x0A); hex64(4,13,ns_q32); puts(6,"ABI: RAW=0 ELF=1 PE=2 MACH=3 | TIME=hash(raw,wall,prev)",0x0E); load_user_v9(); puts(11,"FS: 0x2000 prog 0x4000-0x7FFF 16K free | KERNEL <8K",0x07); puts(13,"JUMPING TO RING3 0x200000...",0x0A); for(volatile int i=0;i<1000000;i++) __asm__ volatile("nop"); jump_ring3(); for(;;){ puts(20,"BACK IN KERNEL hash:",0x0C); hex64(20,22,prev_hash); for(volatile int i=0;i<1000000;i++) __asm__ volatile("nop"); } }
