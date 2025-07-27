package main

import (
	"bufio"
	"fmt"
	"os"
	"os/exec"
	"strings"
)

func main() {
	printBanner()
	for {
		printMenu()
		var choice int
		_, err := fmt.Scan(&choice)
		if err != nil {
			fmt.Println("Invalid input, try again.")
			continue
		}

		switch choice {
		case 1:
			runGoComponent("syn_udp_icmp_flooder")
		case 2:
			runGoComponent("tls_handshake_flood")
		case 3:
			runGoComponent("websocket_client_flood")
		case 4:
			runPythonComponent("../python/main.py")
		case 5:
			runCComponent("icmp_flooder")
		case 6:
			runCComponent("smurf_attack")
		case 7:
			runCComponent("syn_flooder")
		case 8:
			runCComponent("teardrop")
		case 9:
			runCComponent("udp_amplification")
		case 10:
			// Proxy Attacks
			path := prompt("Enter proxy list file path (ip:port per line): ")
			runPythonComponentWithArgs("../python/proxy_manager.py", path)
		case 11:
			// Vector Attacks
			runGoComponent("vector_attacks")
		case 12:
			// All Vector + Proxy Attacks
			proxyPath := prompt("Enter proxy list file path (ip:port per line): ")
			runPythonComponentWithArgs("../python/proxy_manager.py", proxyPath)
			runGoComponent("vector_attacks")
		case 0:
			fmt.Println("Exiting...")
			return
		default:
			fmt.Println("Invalid option, please try again.")
		}
	}
}

func printBanner() {
	fmt.Println(`
███████╗██╗      ██████╗  ██████╗ ██████╗ ██╗  ██╗
██╔════╝██║     ██╔═══██╗██╔═══██╗██╔══██╗╚██╗██╔╝
█████╗  ██║     ██║   ██║██║   ██║██║  ██║ ╚███╔╝ 
██╔══╝  ██║     ██║   ██║██║   ██║██║  ██║ ██╔██╗ 
██║     ███████╗╚██████╔╝╚██████╔╝██████╔╝██╔╝ ██╗
╚═╝     ╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝

FloodX - DDoS Toolkit by Leo
--------------------------------------------
`)
}

func printMenu() {
	fmt.Println(`
Main Menu:
1. SYN/UDP/ICMP Flood (Go)
2. TLS Handshake Flood (Go)
3. WebSocket Flood (Go)
4. Application Layer Attacks (Python)
5. ICMP Flooder (C)
6. Smurf Attack (C)
7. SYN Flooder (C)
8. Teardrop Attack (C)
9. UDP Amplification (C)
10. Proxy Attacks (Python)
11. All Vector Attacks (Go)
0. Exit`)
	fmt.Print("Select an option: ")
}

func prompt(msg string) string {
	reader := bufio.NewReader(os.Stdin)
	fmt.Print(msg)
	input, _ := reader.ReadString('\n')
	return strings.TrimSpace(input)
}

func runGoComponent(component string) {
	fmt.Printf("Compiling and running Go component: %s...\n", component)
	build := exec.Command("go", "build", "-o", component, fmt.Sprintf("../go/%s/main.go", component))
	build.Stdout = os.Stdout
	build.Stderr = os.Stderr
	if err := build.Run(); err != nil {
		fmt.Printf("Error compiling %s: %v\n", component, err)
		return
	}
	run := exec.Command(fmt.Sprintf("./%s", component))
	run.Stdout = os.Stdout
	run.Stderr = os.Stderr
	if err := run.Run(); err != nil {
		fmt.Printf("Error running %s: %v\n", component, err)
	}
}

func runPythonComponent(script string) {
	runPythonComponentWithArgs(script)
}

func runPythonComponentWithArgs(script string, args ...string) {
	cmdArgs := append([]string{script}, args...)
	run := exec.Command("python3", cmdArgs...)
	run.Stdout = os.Stdout
	run.Stderr = os.Stderr
	if err := run.Run(); err != nil {
		fmt.Printf("Error running Python script %s: %v\n", script, err)
	}
}

func runCComponent(component string) {
	fmt.Printf("Compiling and running C component: %s...\n", component)
	build := exec.Command("gcc", fmt.Sprintf("../c_cpp/%s/main.c", component), "-o", component)
	build.Stdout = os.Stdout
	build.Stderr = os.Stderr
	if err := build.Run(); err != nil {
		fmt.Printf("Error compiling %s: %v\n", component, err)
		return
	}
	run := exec.Command(fmt.Sprintf("./%s", component))
	run.Stdout = os.Stdout
	run.Stderr = os.Stderr
	if err := run.Run(); err != nil {
		fmt.Printf("Error running %s: %v\n", component, err)
	}
}
