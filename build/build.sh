#!/bin/bash

# Set up environment variables
export GOPATH=$(pwd)/../src/go
export PATH=$PATH:$(go env GOPATH)/bin

# Create bin directory if it doesn't exist
mkdir -p ../bin

# Compile Go components
echo "Compiling Go components..."
go build -o ../bin/syn_udp_icmp_flooder ../src/go/syn_udp_icmp_flooder/main.go
go build -o ../bin/tls_handshake_flood ../src/go/tls_handshake_flood/main.go
go build -o ../bin/websocket_client_flood ../src/go/websocket_client_flood/main.go

# Compile C components
echo "Compiling C components..."
gcc ../src/c_cpp/icmp_flooder/main.c -o ../bin/icmp_flooder
gcc ../src/c_cpp/syn_flooder/main.c -o ../bin/syn_flooder
gcc ../src/c_cpp/udp_amplification/main.c -o ../bin/udp_amplification
gcc ../src/c_cpp/teardrop/main.c -o ../bin/teardrop

# Compile Python components using PyInstaller
echo "Compiling Python components..."
pyinstaller --onefile --distpath ../bin ../src/python/main.py

echo "All components compiled successfully!"
