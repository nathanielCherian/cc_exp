import paramiko
import time
import os

def connect_client(host, username):
    """Establish an SSH connection to the given host with the specified username."""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Auto accept unknown hosts
        client.connect(hostname=host, username=username)
        return client
    except Exception as e:
        print(f"Failed to connect to {host}: {e}")
        return None

def execute_command(client, command):
    """Execute a command on the remote machine via SSH and return output and errors safely."""
    if client is None:
        print("Invalid SSH client, skipping command execution.")
        return
    
    try:
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode().strip() if stdout else ""
        error = stderr.read().decode().strip() if stderr else ""

        print(f"Executing: {command}")
        if output:
            print(f"Output:\n{output}")
        if error:
            print(f"Error:\n{error}")
    except Exception as e:
        print(f"Failed to execute command '{command}': {e}")

def scp_file(client, remote_path, local_path):
    """SCP a file from the remote server to the local machine."""
    if client is None:
        print("Invalid SSH client, skipping file transfer.")
        return
    
    try:
        # Use SFTP to get the file
        sftp = client.open_sftp()

        # Ensure the local path exists, create if necessary
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        print(f"Transferring {remote_path} to {local_path}...")
        sftp.get(remote_path, local_path)
        print(f"File transferred successfully: {local_path}")

        sftp.close()
    except Exception as e:
        print(f"Failed to SCP file {remote_path} to {local_path}: {e}")

def run_exp():
    """Runs experiment by connecting to multiple nodes and executing commands."""
    hosts = [
        "amd007.utah.cloudlab.us",
        "amd001.utah.cloudlab.us",
        "amd010.utah.cloudlab.us"
    ]
    username = "cheriann"
    
    # Establish SSH connections
    clients = {host: connect_client(host, username) for host in hosts}

    try:
        if clients[hosts[1]]:  # Only execute if connection was successful

            # Starting the bess node
            execute_command(clients[hosts[1]], "./cleanup.sh")
            execute_command(clients[hosts[1]], "./start_bess.sh")

    
            execute_command(clients[hosts[0]], "./kill_server.sh")
            execute_command(clients[hosts[0]], "./start_server.sh")

            time.sleep(2)
            execute_command(clients[hosts[2]], "./download_file.sh datafiles/file_2MB.txt")
            time.sleep(2)

            execute_command(clients[hosts[1]], "./stop_bess.sh")
            time.sleep(1)

            scp_file(clients[hosts[1]], "/users/cheriann/test_file_left.log", "/scratch1/cheriann/SPRING_25/cc_exp/bess_stuff/logs/left.log")
            scp_file(clients[hosts[1]], "/users/cheriann/test_file_right.log", "/scratch1/cheriann/SPRING_25/cc_exp/bess_stuff/logs/right.log")
            # execute_command(clients[hosts[1]], "echo $USER")
            # execute_command(clients[hosts[1]], "./bess/bessctl/bessctl")
            # execute_command(clients[hosts[0]], "uname -a")
            # execute_command(clients[hosts[2]], "pwd")

    finally:
        # Close all SSH connections
        for host, client in clients.items():
            if client:
                client.close()

# Example usage:
if __name__ == "__main__":
    run_exp()
