typedef unsigned long long u64;
#define MAX_USERS 8
struct user{ u64 id; u64 hash; int active; };
static struct user users[MAX_USERS]={{1,0x1111,1},{2,0x2222,1},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0}};
int user_one_check_c(u64 id){ for(int i=0;i<MAX_USERS;i++) if(users[i].active && users[i].id==id) return 0; return -1; }
int user_one_add_c(u64 id, u64 hash){ for(int i=0;i<MAX_USERS;i++) if(!users[i].active){ users[i].id=id; users[i].hash=hash; users[i].active=1; return 0; } return -1; }
