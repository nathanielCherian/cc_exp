#!/usr/bin/python
"""
This is an example how to simulate a client server environment.
"""
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel
import time 
import sys
import threading

if len(sys.argv) < 3:
    print("Error: Need forlder to save pcapcs and cc")
    exit(1)

mounted_folder = sys.argv[1]
congestion_control = sys.argv[2]

setLogLevel('info')


def run_and_stop_capture(textfile, pcap_file, server, client, ind):
    info(f"starting on {server.IP()} - {client.IP()} pair\n")
    server.cmd(f"tshark -i server{ind}-eth0 -w /pcaps/{pcap_file}.pcap &")
    time.sleep(1)
    info("downloading\n")
    info(client.cmd(f"time curl {server.IP()}:8000/{textfile} > /dev/null"))
    time.sleep(2)
    info("ending capture\n")
    server.cmd("pkill -SIGINT tshark")
    info(f"finished {server.IP()} - {client.IP()} pair\n")
    return

def run_exp(textfile, pcap_file, pairs):
    info("starting capture\n")
    threads = []
    for i, pair in enumerate(pairs):
        server, client = pair
        thread = threading.Thread(target=run_and_stop_capture, args=(textfile, "s"+str(i)+"_"+pcap_file, server, client, i+1))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def run(bandwidth, delay, max_queue_size):
    info(f"starting capture for file with {bandwidth=} {delay=} {max_queue_size=}\n")

    net = Containernet(controller=Controller)
    net.addController('c0')

    info('*** Adding server and client container\n')
    server1 = net.addDocker('server1', 
        ip='10.0.0.1', dcmd="python3 -m http.server", dimage="test_server:latest", 
        volumes={mounted_folder: {"bind": "/pcaps/", "mode": "rw"}}, 
        privileged=True)
    server2 = net.addDocker('server2', 
        ip='10.0.0.2', dcmd="python3 -m http.server", dimage="test_server:latest", 
        volumes={mounted_folder: {"bind": "/pcaps/", "mode": "rw"}}, 
        privileged=True)


    client1 = net.addDocker('client1', 
            ip='10.0.0.251', dimage="test_client:latest", 
            volumes={mounted_folder: {"bind": "/pcaps/", "mode": "rw"}},)
    client2 = net.addDocker('client2', 
            ip='10.0.0.252', dimage="test_client:latest", 
            volumes={mounted_folder: {"bind": "/pcaps/", "mode": "rw"}},)


    info('*** Setup network\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    net.addLink(server1, s1, params={"mtu": "1500"})
    net.addLink(server2, s1, params={"mtu": "1500"})
    link = net.addLink(s1, s2, cls=TCLink, delay=f"{delay}ms", bw=bandwidth)
    net.addLink(s2, client1, params={"mtu": "1500"})
    net.addLink(s2, client2, params={"mtu": "1500"})
    net.start()

    info('*** Starting to execute commands\n')

    client1.cmd('ifconfig client1-eth0 mtu 1500 up')
    server1.cmd('ifconfig server1-eth0 mtu 1500 up')
    client2.cmd('ifconfig client2-eth0 mtu 1500 up')
    server2.cmd('ifconfig server2-eth0 mtu 1500 up')

    server_cc = server1.cmd("sysctl net.ipv4.tcp_congestion_control")
    client_cc = client2.cmd("sysctl net.ipv4.tcp_congestion_control")

    info(f"\n\nSERVER CONGESTION CONTROL {server_cc}\nCLIENT CONGESTION CONTROL {client_cc}\n\n")
    pairs = [(server1, client1), (server2, client2)]
    i=1
    run_exp("shakespeare.txt", f"{congestion_control}_{delay}ms_{bandwidth}bw_{i}.pcap", pairs)
    #run_and_stop_capture("shakespeare.txt", 'test.pcap', server1, client1, 100)
    CLI(net)

    net.stop()
    info(f"finished capture for file with {bandwidth=} {delay=} {max_queue_size=}\n")

if __name__ == "__main__":
    run(50, 1, None)
