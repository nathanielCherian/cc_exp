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

if len(sys.argv) < 3:
    print("Error: Need forlder to save pcapcs and cc")
    exit(1)

mounted_folder = sys.argv[1]
congestion_control = sys.argv[2]

setLogLevel('info')


def run_exp(textfile, pcap_file, server, client):
    info("starting capture\n")
    server.cmd(f"tshark -i server-eth0 -w /pcaps/{pcap_file}.pcap &")
    time.sleep(1)
    info("downloading\n")
    info(client.cmd(f"time curl 10.0.0.251:8000/{textfile} > /dev/null"))
    time.sleep(2)
    info("ending capture\n")
    server.cmd("pkill -SIGINT tshark")


def run(bandwidth, delay, max_queue_size):
    info(f"starting capture for file with {bandwidth=} {delay=} {max_queue_size=}\n")

    net = Containernet(controller=Controller)
    net.addController('c0')

    info('*** Adding server and client container\n')
    server = net.addDocker('server', 
        ip='10.0.0.251', dcmd="python3 -m http.server --directory /pcaps/files/", dimage="test_server:latest", 
        volumes={mounted_folder: {"bind": "/pcaps/", "mode": "rw"}}, 
        privileged=True)

    client = net.addDocker('client', 
            ip='10.0.0.252', dimage="test_client:latest", 
            volumes={mounted_folder: {"bind": "/pcaps/", "mode": "rw"}},)

    bgserver = net.addDocker('bgserver', 
        ip='10.0.0.1', dcmd="python3 -m http.server --directory /pcaps/files/", dimage="test_server:latest", 
        volumes={mounted_folder: {"bind": "/pcaps/", "mode": "rw"}}, 
        privileged=True)
    bgclient = net.addDocker('bgclient', 
            ip='10.0.0.2', dimage="test_client:latest", 
            volumes={mounted_folder: {"bind": "/pcaps/", "mode": "rw"}},)


    info('*** Setup network\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    net.addLink(server, s1, params={"mtu": "1500"})
    net.addLink(bgserver, s1, params={"mtu": "1500"})
    link = net.addLink(s1, s2, cls=TCLink, delay=f"{delay}ms", bw=bandwidth, max_queue_size=max_queue_size)
    net.addLink(s2, client, params={"mtu": "1500"})
    net.addLink(s2, bgclient, params={"mtu": "1500"})
    net.start()

    info('*** Starting to execute commands\n')

    client.cmd('ifconfig client-eth0 mtu 1500 up')
    server.cmd('ifconfig server-eth0 mtu 1500 up')

    server_cc = server.cmd("sysctl net.ipv4.tcp_congestion_control")
    client_cc = client.cmd("sysctl net.ipv4.tcp_congestion_control")

    info(f"\n\nSERVER CONGESTION CONTROL {server_cc}\nCLIENT CONGESTION CONTROL {client_cc}\n\n")
    
    # Set a background traffic
    bgclient.cmd(f"curl {bgserver.IP()}:8000/file_1000MB.dat > /dev/null &")


    for i in range(10):
        size = 5
        run_exp(f"file_{size}MB.dat", f"{congestion_control}_{delay}ms_{bandwidth}bw_{max_queue_size}mqs_{size}_{i}", server, client)


    #CLI(net)

    net.stop()
    info(f"finished capture for file with {bandwidth=} {delay=} {max_queue_size=}\n")

if __name__ == "__main__":
    for delay in [6,9,10]:
        for bandwidth in [40,45,50]:
            run(delay, bandwidth, 10)
