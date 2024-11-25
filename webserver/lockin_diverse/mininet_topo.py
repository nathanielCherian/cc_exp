from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import time
import sys

pcap_out_file = "test.pcap"
bw = 10
delay = "10ms"
target_file = "shake_1MB.txt"

if len(sys.argv) > 1:
    pcap_out_file = sys.argv[1]
    bw = float(sys.argv[2])
    delay = sys.argv[3]
    target_file = sys.argv[4]

mounted_folder = "/users/cheriann/cc_exp/webserver/lockin_diverse/mounted_folder/"

def download_with_cap(target_file, pcap_file, server, client):
    info("starting capture\n")
    server.cmd(f"tshark -i h2-eth0 -w {mounted_folder}/pcaps/{pcap_file} &")
    time.sleep(0.5)
    info("wget-ing...\n")
    info(client.cmd(f"wget {server.IP()}:8000/{target_file} -O index"))
    time.sleep(0.5)
    info("ending capture")
    server.cmd("pkill -SIGINT tshark")


def make_bg_client(i):
    return net.addHost(f'c{i}', ip='10.0.1.{i}')

def make_bg_server(i):
    return net.addHost(f'v{i}', ip='10.0.2.{i}')

def experiment():
    setLogLevel('info')
    
    # Initialize the Containernet instance
    net = Mininet(controller=Controller, switch=OVSSwitch, link=TCLink)
    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Adding switches\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')

    info('*** Adding hosts\n')

    client =  net.addHost('h1', ip='10.0.0.1')
    server = net.addHost('h2', ip='10.0.0.2')

    bg_clients = [make_bg_client(i) for i in range(1,4)]
    bg_servers = [make_bg_server(i) for i in range(1,4)]

    info('*** Adding links\n')
    # Connecting client to switch3
    net.addLink(client, s3, intfName1='h1-eth0', cls=TCLink, params1={'mtu': 1500})
    # Connecting server to switch1
    net.addLink(server, s1, intfName1='h2-eth0', cls=TCLink, params1={'mtu': 1500})
    # Connecting the main switches
    net.addLink(s1, s2, cls=TCLink, delay=delay, bw=bw)
    # Connecting switch2 to switch3
    bottleneck_link = net.addLink(s2, s3)

    for c in bg_clients:
        net.addLink(c, s2)
    for s in bg_servers:
        net.addLink(s, s1)

    info('*** Starting network\n')
    net.start()

    # Create the nebby bottleneck between s2 and s3
    s2_iface = bottleneck_link.intf1.name
    s3_iface = bottleneck_link.intf2.name

    # Configure the FIFO qdisc on the bottleneck link
    info('*** Configuring TC settings on bottleneck link\n')
    net.get('s2').cmd(f'tc qdisc add dev {s2_iface} root handle 1: netem delay 50ms')
    net.get('s2').cmd(f'tc qdisc add dev {s2_iface} parent 1:1 handle 10: tbf rate 200kbit burst 1540 limit 20000')
    net.get('s2').cmd(f'tc qdisc add dev {s2_iface} parent 10: bfifo limit 20000')

    net.get('s3').cmd(f'tc qdisc add dev {s3_iface} root handle 1: netem delay 50ms')
    net.get('s3').cmd(f'tc qdisc add dev {s3_iface} parent 1:1 handle 10: tbf rate 200kbit burst 1540 limit 20000')
    net.get('s3').cmd(f'tc qdisc add dev {s3_iface} parent 10: bfifo limit 20000')

    info('*** Verifying TC settings\n')
    info(net.get('s2').cmd(f'tc qdisc show dev {s2_iface}'))
    info(net.get('s3').cmd(f'tc qdisc show dev {s3_iface}'))
       

    info('*** Testing connectivity\n')
    net.pingAll()


    info('*** Starting Server\n')
    server.cmd(f"python3 -m http.server --directory {mounted_folder}/server &")


    info('*** Starting Background Scripts\n')
    server.cmd(f"python3 -m http.server --directory {mounted_folder}/server &")

    #info('*** Starting CLI\n')
    #CLI(net)

    info('*** Testing capture\n')
    download_with_cap(target_file, pcap_out_file, server, client)

    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    experiment()
