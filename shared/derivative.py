import numpy as np
import matplotlib.pyplot as plt

def plot_first_derivative(time_series, values):
    """
    Computes and plots the first derivative of a time series.

    Parameters:
    - time_series: array-like, time points of the data
    - values: array-like, corresponding values of the data
    """
    if len(time_series) != len(values):
        raise ValueError("time_series and values must have the same length.")
    if len(time_series) < 2:
        raise ValueError("At least two points are required to compute the derivative.")

    # Compute the first derivative
    delta_t = np.diff(time_series)  # Time intervals
    delta_v = np.diff(values)       # Value intervals
    first_derivative = delta_v / delta_t

    # Midpoints for plotting the derivative
    midpoints = (time_series[:-1] + time_series[1:]) / 2

    # Plot the original time series and the derivative
    plt.figure(figsize=(10, 5))

    # Original time series
    plt.subplot(1, 2, 1)
    plt.plot(time_series, values, marker='o', label='Original Data')
    plt.xlabel('Time')
    plt.ylabel('Values')
    plt.title('Original Time Series')
    plt.grid()
    plt.legend()

    # First derivative
    plt.subplot(1, 2, 2)
    plt.plot(midpoints, first_derivative, marker='o', color='orange', label='First Derivative')
    plt.xlabel('Time (Midpoints)')
    plt.ylabel('Derivative')
    plt.title('First Derivative')
    plt.grid()
    plt.legend()

    plt.tight_layout()
    plt.show()


def split_time_series_on_anomalies(time_series, values, method='iqr'):
    if len(time_series) != len(values):
        raise ValueError("time_series and values must have the same length.")
    if len(time_series) < 2:
        raise ValueError("At least two points are required to compute the derivative.")

    # Compute the first derivative
    delta_t = np.diff(time_series)
    delta_v = np.diff(values)
    first_derivative = delta_v / delta_t

    # Detect outliers
    if method == 'iqr':
        # Interquartile Range (IQR) method
        q1 = np.percentile(first_derivative, 25)
        q3 = np.percentile(first_derivative, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
    elif method == 'zscore':
        # Z-score method
        mean = np.mean(first_derivative)
        std_dev = np.std(first_derivative)
        z_scores = (first_derivative - mean) / std_dev
        lower_bound = -3  # Focus on segments below 3 standard deviations
    else:
        raise ValueError("Method must be either 'iqr' or 'zscore'.")

    # Identify indices of anomalous points
    if method == 'iqr':
        anomalous_indices = np.where(first_derivative < lower_bound)[0]
    elif method == 'zscore':
        anomalous_indices = np.where(z_scores < lower_bound)[0]

    # Add boundaries for splitting
    split_points = [0] + (anomalous_indices + 1).tolist() + [len(time_series)]

    # Split the time series and values into intervals
    intervals = [
        (time_series[start:end], values[start:end])
        for start, end in zip(split_points[:-1], split_points[1:])
    ]

    return intervals
