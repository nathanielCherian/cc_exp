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


setLogLevel('info')

net = Containernet(controller=Controller)
net.addController('c0')

info('*** Adding server and client container\n')
server = net.addDocker('server', ip='10.0.0.251', dcmd="python3 -m http.server", dimage="test_server:latest", sysctl={'net.ipv4.tcp_congestion_control': 'reno'}, volumes={"/users/cheriann/cc_exp/webserver/pcaps": {"bind": "/pcaps/", "mode": "rw"}}, privileged=True)
client = net.addDocker('client', ip='10.0.0.252', dimage="test_client:latest", volumes={"/users/cheriann/cc_exp/webserver/pcaps": {"bind": "/pcaps/", "mode": "rw"}},)

info('*** Setup network\n')
s1 = net.addSwitch('s1')
s2 = net.addSwitch('s2')
net.addLink(server, s1, params={"mtu": "1500"})
link = net.addLink(s1, s2, cls=TCLink, delay='10ms', bw=50, max_queue_size=10)
net.addLink(s2, client, params={"mtu": "1500"})
net.start()

info('*** Starting to execute commands\n')

client.cmd('ifconfig client-eth0 mtu 1500 up')
server.cmd('ifconfig server-eth0 mtu 1500 up')

def run_exp(filename):
    info("starting capture\n")
    server.cmd(f"tshark -i server-eth0 -w /pcaps/{filename}.pcap &")
    time.sleep(1)
    info("downloading\n")
    info(client.cmd(f"time curl 10.0.0.251:8000/{filename} > /dev/null"))
    time.sleep(2)
    info("ending capture\n")
    client.cmd("pkill -SIGINT tshark")

run_exp("shakespeare.txt")

CLI(net)

net.stop()
