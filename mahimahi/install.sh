#!/bin/bash

# Update package lists
echo "Updating package lists..."
sudo apt update

# Install dependencies
echo "Installing dependencies..."
sudo apt install -y \
    protobuf-compiler \
    libprotobuf-dev \
    autotools-dev \
    dh-autoreconf \
    iptables \
    pkg-config \
    dnsmasq-base \
    apache2-bin \
    debhelper \
    libssl-dev \
    ssl-cert \
    libxcb-present-dev \
    libcairo2-dev \
    libpango1.0-dev \
    apache2-dev

# Installation complete
echo "All dependencies installed successfully!"

git clone https://github.com/ravinet/mahimahi

cd mahimahi

./autogen.sh

./configure

make

sudo make install
