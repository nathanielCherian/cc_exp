import csv
import os
from scapy.all import rdpcap, IP, TCP
import sys
from joblib import Parallel, delayed

def parse_pcap_to_csv(pcap_file):
    output_file = os.path.join("temp.csv")
    with open(output_file, mode='w', newline='') as csv_file:
        fieldnames = [
            "_ws.col.Time", "frame.time_relative", "tcp.time_relative", "frame.number", "frame.len",
            "ip.src", "tcp.srcport", "ip.dst", "tcp.dstport", "tcp.len", "tcp.seq", "tcp.ack"
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        
        # Read the pcap file using scapy
        packets = rdpcap(pcap_file)

        for i, packet in enumerate(packets):
            if IP in packet and TCP in packet:
                # Prepare the data to write to CSV
                data = {
                    "_ws.col.Time": packet.time,  # Timestamp of the packet
                    "frame.time_relative": packet.time - packets[0].time,  # Time relative to the first packet
                    "tcp.time_relative": packet.time - packets[0].time,  # Assuming the same as frame time here
                    "frame.number": i + 1,  # Frame number (index + 1)
                    "frame.len": len(packet),  # Length of the packet
                    "ip.src": packet[IP].src,  # Source IP
                    "tcp.srcport": packet[TCP].sport,  # Source port
                    "ip.dst": packet[IP].dst,  # Destination IP
                    "tcp.dstport": packet[TCP].dport,  # Destination port
                    "tcp.len": len(packet[TCP].payload),  # Length of TCP payload
                    "tcp.seq": packet[TCP].seq,  # TCP sequence number
                    "tcp.ack": packet[TCP].ack,  # TCP acknowledgment number
                }
                writer.writerow(data)

import csv
import os
from scapy.all import rdpcap, IP, TCP
import sys
from joblib import Parallel, delayed
import pandas as pd
import numpy as np

def three_tuple(row):
    ips = [row['ip.src'], row['ip.dst']]
    ports = [str(row['tcp.srcport']), str(row['tcp.dstport'])]
    ips.sort()
    ports.sort()
    return ','.join(ips)+","+",".join(ports)

def five_tuple(row):
    return row['ip.src']+","+str(row['tcp.srcport'])+","+row['ip.dst']+","+str(row['tcp.dstport'])

def create_rel_seq_ack(d):
    min_ack = d['tcp.ack'].replace(0, np.inf).min()
    min_seq = d['tcp.seq'].replace(0, np.inf).min()
    d['rel_seq'] = (d['tcp.seq'] - min_seq).clip(lower=0).astype(np.int64)
    d['rel_ack'] = (d['tcp.ack'] - min_ack).clip(lower=0).astype(np.int64)
    return d

def process_worker(filepath):
    filename = os.path.basename(filepath)
    if not filename.endswith(".csv"):
        return None
    df = pd.read_csv(filepath)
    df.dropna(inplace=True)
    df['ftc'] = df.apply(five_tuple, axis=1)
    df['filename'] = filename
    df['five_tuple'] = df.apply(five_tuple, axis=1)
    df['three_tuple'] = df.apply(three_tuple, axis=1)
    rel_df = df.groupby('ftc', group_keys=False).apply(create_rel_seq_ack, include_groups=False)
    #grouped = rel_df.groupby('five_tuple')
    grouped = rel_df.groupby('three_tuple')
    return [(gv, gdf) for gv, gdf in grouped]

from shared import bif

def bif_worker(d, src_ip, dst_ip):
    d['frame.time_relative'] = d['frame.time_relative'] - d['frame.time_relative'].iloc[0]
    times, bytes_in_flight = bif.bif_df(d, src_ip, dst_ip)
    return (times, bytes_in_flight)



from shared import bif

def do_for_my_file(filename):
    parse_pcap_to_csv(filename)
    groups = process_worker("temp.csv")
    times, bif_vals = bif_worker(groups[0][1], "10.0.0.2", "10.0.0.1")
    smooth_vals, smooth_times = bif.create_fft(times, bif_vals, 0.200)
    # bif.plot_bif(bif_vals, times)
    bif.plot_bif(smooth_vals, smooth_times)

def akhil_function(filename):
    parse_pcap_to_csv(filename)
    print("done parse")
    groups = process_worker("temp.csv")
    print("done process")
    good_samples = [(i, k) for i, k in groups if "10.0.0.1,10.0.1.7," in i and "10.0.0.1,10.0.1.7,21" not in i]
    # good_samples = [(i, k) for i, k in groups if "10.0.0.1,10.0.0.2," in i and "10.0.0.1,10.0.0.2,21" not in i]
    print([i for i, _ in good_samples])
    lengths = [len(d) for _, d in good_samples]
    print(lengths)
    for i in range(len(good_samples)):
        if len(good_samples[i][1]) > 200:
            times, bif_vals = bif_worker(good_samples[i][1], "10.0.1.7", "10.0.0.1")
            # times, bif_vals = bif_worker(good_samples[i][1], "10.0.0.2", "10.0.0.1")
            bif.plot_bif(bif_vals, times, title=good_samples[i][0])
