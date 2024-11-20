import numpy as np
import matplotlib.pyplot as plt

def create_time_delay_embedding(lin_times, values, lag_factor, dims, sample_rate=1):
    time_delta = lin_times[1] - lin_times[0]
    new_data = []
    for i in range(len(lin_times) - dims*lag_factor):
        if i % sample_rate == 0:
            new_data.append([values[i+d*lag_factor] for d in range(dims)])
    return np.array(new_data)

def plot_scatter(x, y, title="Embedding", xlabel="X-axis", ylabel="Y-axis", save_path=None):
    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, color='blue', marker='o')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    
    if save_path:
        plt.savefig(save_path, format='png', dpi=300)
        # print(f"Plot saved to {save_path}")
    else:
        plt.show()
    plt.close() 