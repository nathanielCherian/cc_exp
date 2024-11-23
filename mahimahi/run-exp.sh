#!/bin/bash

# Check if a file is provided as an argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <filename>"
    exit 1
fi

# File to read
file="$1"

# Check if the file exists
if [ ! -f "$file" ]; then
    echo "Error: File '$file' not found!"
    exit 1
fi

# Loop through each line in the file
while IFS= read -r line; do
    # Extract the 3rd column (space-separated)
    num=$(echo "$line" | awk '{print $1}')
    base=$(echo "$line" | awk '{print $2}')
    url=$(echo "$line" | awk '{print $3}')
    
    # Skip if the column is empty
    if [ -n "$url" ]; then
	echo "starting exp for $base ($url)"
        ./run_test.sh sample-test 1 50 200 2 $url
	if [ -f test.pcap ]; then
		mv test.pcap outputs/$base.pcap
		mv index outputs/$base.data
	fi
    else
        echo "No URL found in line: $line"
    fi
done < "$file"
