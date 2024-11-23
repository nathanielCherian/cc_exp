import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt

def calculate_bps(filename,sender_ip, receiver_ip, interval=1.0):
    # Convert data into a DataFrame if it's not already one
    df = pd.read_csv(filename)
    df = df[ (df['ip.src'] == sender_ip) | (df['ip.src'] == receiver_ip)]
    
    # Set 'frame.time_relative' as the DataFrame's index and convert it to a timedelta for resampling
    df['frame.time_relative'] = pd.to_timedelta(df['frame.time_relative'], unit='s')
    df.set_index('frame.time_relative', inplace=True)
    
    # Use resample to group by the specified interval and sum 'frame.len' within each interval
    bytes_per_interval = df['frame.len'].resample(f'{interval}s').sum()

    # Convert the result to arrays
    times = bytes_per_interval.index.total_seconds()  # Convert TimedeltaIndex to seconds
    bytes_per_interval = bytes_per_interval.values
    
    return times, bytes_per_interval


def plot_bps(times, bytes_per_interval):
    plt.figure(figsize=(10, 6))
    plt.plot(times, bytes_per_interval, marker='o', linestyle='-', color='skyblue', label='Bytes per Second')
    
    plt.xlabel('Time (seconds)')
    plt.ylabel('Bytes per Second')
    plt.title('Bytes per Second over Time')
    plt.grid(axis='both', linestyle='--', alpha=0.7)
    plt.legend()
    plt.show()
