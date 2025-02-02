from scapy.all import rdpcap
import hashlib
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np


def print_pcap_packets(file_path, direction=None):
    packets = rdpcap(file_path)  # Read the pcap file
    
    for packet in packets:
        if hasattr(packet, 'time'):
            if direction and packet['Ether'].src != direction:
                continue
            print(f"Time: {packet.time} - Packet: {packet.summary()} - Size ({len(packet)}")
            if packet.haslayer('IP'):
                # payload = bytes(packet['Raw'].load)
                payload = bytes(packet['IP'].payload)
                hash_value = hashlib.sha256(payload).hexdigest()
                print("\t", hash_value)
        else:
            print(f"Packet: {packet.summary()}")

def print_mac_addresses(file_path):
    packets = rdpcap(file_path)  # Read the pcap file
    for packet in packets:
        if packet.haslayer('Ether'):
            print(f"Source MAC: {packet['Ether'].src}, Destination MAC: {packet['Ether'].dst}")



"""
Assume that the packets we are tracking hit the capture for file1 and then hit file2, src_mac is where they come from 
"""
def get_match_intervals(file1, file2, src_mac):
    packet_exit_times = {}
    
    f2_packets = rdpcap(file2)  # Read the pcap file
    for packet in f2_packets:
        if packet.haslayer('IP') and packet['Ether'].src == src_mac: # Verify it is in the right direction
            payload = bytes(packet['IP'].payload)
            hash_value = hashlib.sha256(payload).hexdigest()
            if hash_value in packet_exit_times:
                raise Exception("Collision!")
            packet_exit_times[hash_value] = float(packet.time)
            
    intervals = []
    f1_packets = rdpcap(file1)
    for packet in f1_packets:
        if packet.haslayer('IP') and packet['Ether'].src == src_mac: # Find packets from cap1 to see if they are in cap2
            payload = bytes(packet['IP'].payload)
            hash_value = hashlib.sha256(payload).hexdigest()
            enter_time = float(packet.time)
            packet_size = len(packet)
            if hash_value not in packet_exit_times:
                intervals.append((enter_time, -1, -1, packet_size))
                #raise Exception("Never left!")
                continue
            exit_time = packet_exit_times[hash_value]
            delta = exit_time - enter_time
            intervals.append((enter_time, exit_time, delta, packet_size))
    return intervals


def get_queue_size(intervals):
    start_time = intervals[0][0]
    end_time = max([r[1] for r in intervals])
    delta = 0.010
    queue = 0
    queue_sizes = [queue, ]

    parts = []
    for i in intervals:
        if i[1] < 0:
            continue
        parts.append((i[0], 0, i[3]))
        parts.append((i[1], 1, i[3]))
    parts.sort()

    nts = np.arange(start_time, end_time+delta, delta)
    for new_time in nts:
        while parts and parts[0][0] <= new_time:
            _, direction, size = parts.pop(0)
            if direction == 0:
                queue += size
            else:
                queue -= size
        queue_sizes.append(queue)

    return queue_sizes

def plot_qs(qs):
    # Create a line plot
    plt.plot([0.01 * i for i in range(len(qs))], qs)
    
    # Add labels and title
    plt.xlabel('Time')
    plt.ylabel('Bytes')
    plt.title('Queue Size')
    
    # Show the plot
    plt.show()


"""
Example Usage:
intervals = get_match_intervals("pcaps/1mb_cubic/eth2.pcap", "pcaps/1mb_cubic/eth1.pcap", "00:00:00:00:03:02")
qs = get_queue_size(intervals)
plot_qs(qs)
"""
