#!/bin/bash

# Set up environment variables
export PATH=$PATH:$(pwd)/../bin

print_banner() {
  cat <<'EOF'

███████╗██╗      ██████╗  ██████╗ ██████╗ ██╗  ██╗
██╔════╝██║     ██╔═══██╗██╔═══██╗██╔══██╗╚██╗██╔╝
█████╗  ██║     ██║   ██║██║   ██║██║  ██║ ╚███╔╝ 
██╔══╝  ██║     ██║   ██║██║   ██║██║  ██║ ██╔██╗ 
██║     ███████╗╚██████╔╝╚██████╔╝██████╔╝██╔╝ ██╗
╚═╝     ╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝

FloodX - Unified Network Stress by Leo
--------------------------------------------
EOF
}

print_menu() {
  cat <<EOF

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
11. Vector Attacks (Go)
0. Exit

EOF
  echo -n "Select an option: "
}

print_banner
while true; do
  print_menu
  read -r choice
  case $choice in
    1)  echo "Running SYN/UDP/ICMP Flooder…"
        ./syn_udp_icmp_flooder ;;
    2)  echo "Running TLS Handshake Flooder…"
        ./tls_handshake_flood ;;
    3)  echo "Running WebSocket Flooder…"
        ./websocket_client_flood ;;
    4)  echo "Running Application Layer Attacks…"
        ./main ;;
    5)  echo "Running ICMP Flooder…"
        ./icmp_flooder ;;
    6)  echo "Running Smurf Attack…"
        ./smurf_attack ;;
    7)  echo "Running SYN Flooder…"
        ./syn_flooder ;;
    8)  echo "Running Teardrop Attack…"
        ./teardrop ;;
    9)  echo "Running UDP Amplification…"
        ./udp_amplification ;;
   10)  echo "Running Proxy Attacks…"
        # e.g. if your Python proxy script is proxy_manager.py
        python3 ../src/python/proxy_manager.py ;;
   11)  echo "Running Vector Attacks…"
        ./vector_attacks -mode=http -target http://example.com ;;
    0)  echo "Exiting…"
        exit 0 ;;
    *)  echo "Invalid option, please try again." ;;
  esac
done
