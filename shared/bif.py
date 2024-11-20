import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def bif(filename, sender_ip, receiver_ip):
    df = pd.read_csv(filename)
    bytes_in_flight = []
    times = []
    most_sent = 0
    most_ack = 0
    for index, row in df.iterrows():
        if pd.notna(row['ip.src']) and pd.notna(row['tcp.seq']) and pd.notna(row['tcp.ack']):
            if sender_ip == row['ip.src']:
                most_sent = max(most_sent, int(row["tcp.seq"]))
            if receiver_ip == row['ip.src']:
                most_ack = max(most_ack, int(row["tcp.ack"]))
            bytes_in_flight.append(max(most_sent - most_ack, 0))
            times.append(row['frame.time_relative'])
    return times, bytes_in_flight

def bif_df_normal(df, sender_ip, receiver_ip):
    bytes_in_flight = []
    times = []
    most_sent = 0
    most_ack = 0
    for index, row in df.iterrows():
        if pd.notna(row['ip.src']) and pd.notna(row['tcp.seq']) and pd.notna(row['tcp.ack']):
            if sender_ip == row['ip.src']:
                most_sent = max(most_sent, int(row["tcp.seq"]))
            if receiver_ip == row['ip.src']:
                most_ack = max(most_ack, int(row["tcp.ack"]))
            bytes_in_flight.append(max(most_sent - most_ack, 0))
            times.append(row['frame.time_relative'])
    return times, bytes_in_flight



def bif_df(df, sender_ip, receiver_ip):
    bytes_in_flight = []
    times = []
    most_sent = 0
    most_ack = 0
    for index, row in df.iterrows():
        if pd.notna(row['ip.src']) and pd.notna(row['rel_seq']) and pd.notna(row['rel_ack']):
            if sender_ip == row['ip.src']:
                most_sent = max(most_sent, int(row["rel_seq"]))
            if receiver_ip == row['ip.src']:
                most_ack = max(most_ack, int(row["rel_ack"]))
            bytes_in_flight.append(max(most_sent - most_ack, 0))
            times.append(row['frame.time_relative'])
    return times, bytes_in_flight




def create_fft(times, values, rtt):
    # Interpolate points
    lin_times = np.linspace(times[0], times[-1], len(values))
    int_vals = np.interp(lin_times, times, values)

    # Perform FFT on the values
    fft_values = np.fft.fft(int_vals)
    fft_freqs = np.fft.fftfreq(len(values), d=(lin_times[1] - lin_times[0]))
    
    # Zero out components above the cutoff frequency
    fft_values[np.abs(fft_freqs) > (1/rtt)] = 0
    
    # Perform the inverse FFT to get the filtered time series
    filtered_values = np.fft.ifft(fft_values).real 
    
    return filtered_values, lin_times

def plot_bif(values, times, title=None, save_path=None):
    plt.figure(figsize=(10, 5))
    plt.plot(times, values, linestyle='-', color='b')
    plt.xlabel("Time (s)")
    plt.ylabel("Bytes in Flight")
    if title:
        plt.title(title)
    else:    
        plt.title("Bytes in Flight over Time")
    plt.xticks(rotation=45)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()
