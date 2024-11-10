import os
import random
import string
import sys

def generate_random_file(directory, filename, size_in_mb):
    """Generate a file with random content of specified size in MB."""
    filepath = os.path.join(directory, filename)
    size_in_bytes = size_in_mb * 1024 * 1024
    
    with open(filepath, 'wb') as f:
        # Write random data in chunks of 1 MB
        for _ in range(size_in_mb):
            f.write(os.urandom(1024 * 1024))  # Write 1 MB at a time
    print(f"Generated {filename} of size {size_in_mb}MB")

def create_files_in_directory(directory, file_sizes):
    """Create multiple files in the target directory with specified sizes."""
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    for i, size in enumerate(file_sizes):
        filename = f"file_{size}MB.dat"
        generate_random_file(directory, filename, size)

# Specify the target directory and file sizes
target_directory = sys.argv[1]
file_sizes = [5, 10, 50, 100, 200, 300, 1000]  # Sizes in MB

# Generate files
create_files_in_directory(target_directory, file_sizes)
