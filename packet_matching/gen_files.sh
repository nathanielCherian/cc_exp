#!/bin/bash

mkdir datafiles
mkdir pcaps
# Function to generate a file of a specific size
generate_file() {
    size=$1
    filename=$2
    dd if=/dev/urandom of="datafiles/$filename" bs=1K count="$size" status=none
    echo "Generated file $filename of size ${size}KB"
}

# Generate files of different sizes
generate_file 100 "file_100KB.txt"
generate_file 500 "file_500KB.txt"
generate_file 1024 "file_1MB.txt"
generate_file 2048 "file_2MB.txt"

echo "Files generated successfully!"
