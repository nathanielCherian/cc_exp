import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def scatterplot(filename, sender_ip, receiver_ip):
    # Extract the time and packet size (frame.len or tcp.len)
    df = pd.read_csv(filename)
    fdf = df[( (df['ip.src'] == sender_ip) & (df['ip.dst'] == receiver_ip) ) | ( (df['ip.src'] == receiver_ip) & (df['ip.dst'] == sender_ip) )]
    time_array = fdf['frame.time_relative'].values
    packet_size_array = fdf['tcp.len'].values  # Use 'tcp.len' if needed
    # Stack the arrays vertically into a 2xN numpy array
    result = np.vstack((time_array, packet_size_array))
    return result

def plot_scatter(arr, save_path=None):
    # Extract the time and packet size arrays from the numpy array
    time_array = arr[0]
    packet_size_array = arr[1]

    # Create the scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(time_array, packet_size_array)

    # Adding labels and title
    plt.xlabel('Time')
    plt.ylabel('Packet Size (Bytes)')
    plt.title('Packet Size over Time')

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()

def process_directory(directory_path, sender_ip, receiver_ip):
    # Dictionary to store output arrays with filenames as keys
    result_dict = {}

    # Loop through each file in the directory
    for filename in os.listdir(directory_path):
        # Check if the file is a CSV file
        if filename.endswith(".csv"):
            # Full path to the file
            filepath = os.path.join(directory_path, filename)

            # Call the scatterplot function and store the result
            output_array = scatterplot(filepath, sender_ip, receiver_ip)

            # Store the output array in the dictionary with the filename as the key
            result_dict[filename] = output_array

    return result_dict