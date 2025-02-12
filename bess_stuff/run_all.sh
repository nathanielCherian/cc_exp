#!/bin/bash

# Define the possible values
BW_VALUES=(5 10 15)
RTT_VALUES=(40 80 120)
QUEUE_VALUES=(16 32 128)

# Loop through all combinations
for BW in "${BW_VALUES[@]}"; do
    for RTT in "${RTT_VALUES[@]}"; do
        for QUEUE in "${QUEUE_VALUES[@]}"; do
            echo "Running experiment with BW=$BW Mbps, RTT=$RTT ms, Queue Size=$QUEUE packets"
            # Replace the following line with your actual command
            # ./run_experiment --bw $BW --rtt $RTT --queue $QUEUE
            new_dir_name=all_logs/logs_${BW}bw_${QUEUE}q_${RTT}rtt

            mkdir $new_dir_name
            python run_exp.py $BW $QUEUE $RTT
            mv logs/* $new_dir_name
        done
    done
done
