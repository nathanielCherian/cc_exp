import paramiko
import time
import os
import sys

WAIT_TIME=120

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

    bw_mbps = int(sys.argv[1])
    q_size = int(sys.argv[2])
    rtt = int(sys.argv[3])

    #print(bw_mbps, q_size, rtt)

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

            # Update bess_config on the bess node
            execute_command(clients[hosts[1]], f"python update_bess_config.py --bw_mbps {bw_mbps} --q_size_packets {q_size} --rtt {rtt}")

            # Starting the bess node
            execute_command(clients[hosts[1]], "./cleanup.sh")
            print("Done cleaning up")
            execute_command(clients[hosts[1]], "./start_bess.sh")
            print("bess started")
    
            #execute_command(clients[hosts[0]], "./kill_server.sh")
            #execute_command(clients[hosts[0]], "./start_server.sh")


            # Starting scream receiver
            execute_command(clients[hosts[2]], "./kill_scream.sh")
            execute_command(clients[hosts[2]], "./start_scream.sh")

            time.sleep(2)

            # Starting scream sender
            execute_command(clients[hosts[0]], "./kill_scream.sh")
            execute_command(clients[hosts[0]], "./start_scream.sh")

            print("wait time")
            time.sleep(WAIT_TIME)
            print("going to stop everything now")


            # Stopping scream sender
            execute_command(clients[hosts[0]], "./kill_scream.sh")

            # Stopping scream receiver
            execute_command(clients[hosts[2]], "./kill_scream.sh")

            time.sleep(5)

            execute_command(clients[hosts[1]], "./stop_bess.sh")
            time.sleep(1)

            scp_file(clients[hosts[1]], "/users/cheriann/test_file_left.log", "/scratch1/cheriann/SPRING_25/cc_exp/bess_stuff/logs/left.log")
            scp_file(clients[hosts[1]], "/users/cheriann/test_file_right.log", "/scratch1/cheriann/SPRING_25/cc_exp/bess_stuff/logs/right.log")

            scp_file(clients[hosts[1]], "/users/cheriann/left_in.pcap", "/scratch1/cheriann/SPRING_25/cc_exp/bess_stuff/logs/left_in.pcap")
            scp_file(clients[hosts[1]], "/users/cheriann/right_in.pcap", "/scratch1/cheriann/SPRING_25/cc_exp/bess_stuff/logs/right_in.pcap")

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
