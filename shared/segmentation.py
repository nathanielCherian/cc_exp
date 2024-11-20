import numpy as np
import pandas as pd

def split_time_series(time_series, values, interval_size, discard_excess=True):
    if len(time_series) != len(values):
        raise ValueError("time_series and values must have the same length.")
    
    # Convert inputs to numpy arrays
    time_series = np.array(time_series)
    values = np.array(values)
    
    # Determine the start and end times
    start_time = time_series.min()
    end_time = time_series.max()
    
    intervals = []
    current_start = start_time
    
    while current_start < end_time:
        current_end = current_start + interval_size
        
        # Use a mask to find all data points in the current interval
        mask = (time_series >= current_start) & (time_series < current_end)
        interval_time_series = time_series[mask]
        interval_values = values[mask]

        interval_time_series = interval_time_series - np.min(interval_time_series)
        
        if len(interval_time_series) > 0:
            intervals.append((interval_time_series, interval_values))
        
        current_start = current_end
    
    if discard_excess:
        # Remove the last interval if it has incomplete data
        if len(intervals) > 0 and len(intervals[-1][0]) < interval_size:
            intervals.pop()
    
    return intervals


import numpy as np

def interpolate_time_series(times, values, num_points):
    if len(times) != len(values):
        raise ValueError("The lengths of 'times' and 'values' must match.")
    if num_points <= 0:
        raise ValueError("The number of points must be greater than 0.")

    # Create evenly spaced time points
    interpolated_times = np.linspace(times[0], times[-1], num_points)
    
    # Interpolate the values at the new time points
    interpolated_values = np.interp(interpolated_times, times, values)
    
    return interpolated_times, interpolated_values
