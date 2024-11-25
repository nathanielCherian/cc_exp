#!/bin/bash

# List of congestion controls to iterate through
congestion_controls=("reno" "cubic" "bbr" )
bandwidths=("18" "19" "20" "23")
delays=("8ms" "10ms" "11ms" "12ms")
target_files=("shake_1MB.txt" "shake_500KB.txt" "shake_750KB.txt")
# Loop through each congestion control
for cc in "${congestion_controls[@]}"
do
    echo "Changing congestion control to $cc"
    
    # Set the active congestion control
    sysctl -w net.ipv4.tcp_congestion_control=$cc
    
    for bw in "${bandwidths[@]}"
    do
    	for delay in "${delays[@]}" 
	do
    	    for target_file in "${target_files[@]}" 
	    do
	        for i in {1..3}
	        do
		echo "Running with argument ${cc}_${i}.pcap"
		    python us_nebby.py "${cc}_${i}_${bw}_${delay}_${target_file}.pcap" ${bw} ${delay} ${target_file}
		done
	    done
	done
    done
    # Run the do.py script 100 times with the appropriate argument
done
