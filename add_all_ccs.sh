#!/bin/bash

# Check if required permissions
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root. Use sudo."
   exit 1
fi

# Add congestion control algorithms to the kernel
echo "Adding cubic, bbr, and reno to available congestion controls..."

# Load modules if they are not already loaded
modprobe tcp_bbr 2>/dev/null || echo "BBR module not available."
modprobe tcp_cubic 2>/dev/null || echo "Cubic module not available."

# Set the available congestion control algorithms
sysctl -w net.ipv4.tcp_allowed_congestion_control="cubic bbr reno"
sysctl -w net.ipv4.tcp_available_congestion_control="cubic bbr reno"

# Optional: Set the default congestion control (e.g., cubic)
sysctl -w net.ipv4.tcp_congestion_control="cubic"

# Verify the settings
echo "Current congestion control settings:"
sysctl net.ipv4.tcp_allowed_congestion_control
sysctl net.ipv4.tcp_available_congestion_control
sysctl net.ipv4.tcp_congestion_control

echo "Done."

