#!/bin/bash

# List of congestion controls to iterate through
congestion_controls=("reno" "cubic" "bbr" )

# Loop through each congestion control
for cc in "${congestion_controls[@]}"
do
    echo "Changing congestion control to $cc"
    
    # Set the active congestion control
    sysctl -w net.ipv4.tcp_congestion_control=$cc
    
    # Run the do.py script 100 times with the appropriate argument
    for i in {1..20}
    do
        echo "Running with argument ${cc}_${i}.pcap"
        python us_nebby.py "${cc}_${i}.pcap"
    done
done
