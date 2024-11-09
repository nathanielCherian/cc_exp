import os

def generate_large_file(directory="large_files", file_name="large_file", size_gb=10):
    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)
    
    # Define the full path for the file
    file_path = os.path.join(directory, f"{file_name}_{size_gb}GB.dat")
    
    # Calculate the number of bytes for the specified size in GB
    size_bytes = size_gb * 1024 * 1024 * 1024
    
    # Write the file with the specified size
    with open(file_path, "wb") as f:
        f.seek(size_bytes - 1)
        f.write(b'\0')
    
    print(f"Generated file: {file_path} of size {size_gb}GB")

# Create a 10GB and 1GB file as per the requirements
generate_large_file(size_gb=10)
generate_large_file(size_gb=1)

