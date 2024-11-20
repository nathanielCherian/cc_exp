from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import random
import os
import numpy as np
from joblib import Parallel, delayed
import pandas as pd

def parallel_apply(data, func, n_jobs=-1, axis=0):
    # Split data into chunks
    num_chunks = n_jobs if n_jobs > 0 else 10  # Default to 4 if n_jobs is not specified
    data_split = np.array_split(data, num_chunks)
    
    # Function to process each chunk
    def process_chunk(chunk):
        return chunk.apply(func, axis=axis) if isinstance(chunk, pd.DataFrame) else chunk.apply(func)

    # Parallelize the apply operation
    results = Parallel(n_jobs=n_jobs)(delayed(process_chunk)(chunk) for chunk in data_split)
    
    # Concatenate the results back together
    return pd.concat(results)


def process_directory(directory_path, function, *args, **kwargs):
    # Dictionary to store output arrays with filenames as keys
    result_dict = {}

    def pdworker(filename):
       if filename.endswith(".csv"):
          filepath = os.path.join(directory_path, filename)
          output_array = function(filepath, *args, **kwargs)
          return (filename, output_array)

    data = Parallel(n_jobs=-1)(delayed(pdworker)(filename) for filename in os.listdir(directory_path))
    for k, v in data:
      result_dict[k] = v
    return result_dict

def train_test_split(data, labels, test_size=0.2, random_seed=None):
    if random_seed is not None:
        random.seed(random_seed)
    
    # Ensure data and labels are the same length
    if len(data) != len(labels):
        raise ValueError("Data and labels must be of the same length.")
    
    # Get indices and shuffle them
    indices = list(range(len(data)))
    random.shuffle(indices)
    
    # Calculate the number of test samples
    test_count = int(len(data) * test_size)
    
    # Split indices for training and test sets
    test_indices = indices[:test_count]
    train_indices = indices[test_count:]
    
    # Split data and labels based on indices
    X_train = [data[i] for i in train_indices]
    X_test = [data[i] for i in test_indices]
    y_train = [labels[i] for i in train_indices]
    y_test = [labels[i] for i in test_indices]
    
    return X_train, X_test, y_train, y_test



def plot_vectors_with_labels(vectors, labels, n_components=2):
    # Initialize PCA and reduce dimensionality
    pca = PCA(n_components=n_components)
    transformed_vectors = pca.fit_transform(vectors)
    
    # Set up the plot
    labels = np.array(labels)
    unique_labels = np.unique(labels)
    
    plt.figure(figsize=(8, 6))
    plt.scatter(transformed_vectors[:, 0], transformed_vectors[:, 1])
    
    for i, label in enumerate(unique_labels):
        idx = labels == label
        plt.scatter(transformed_vectors[idx, 0], transformed_vectors[idx, 1], 
                    label=label)
    plt.legend()
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.title("2D PCA Projection")
