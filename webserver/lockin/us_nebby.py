from mininet.net import Containernet
from mininet.node import Controller, OVSSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import time
import sys

pcap_out_file = "test.pcap"
if len(sys.argv) > 1:
    pcap_out_file = sys.argv[1]


mounted_folder = "/users/cheriann/cc_exp/webserver/lockin/mounted_folder/"

def download_with_cap(target_file, pcap_file, server, client):
    info("starting capture\n")
    server.cmd(f"tshark -i h2-eth0 -w /mounted/pcaps/{pcap_file} &")
    time.sleep(0.5)
    info("wget-ing...\n")
    info(client.cmd(f"wget {server.IP()}:8000/{target_file} -O index"))
    time.sleep(0.5)
    info("ending capture")
    server.cmd("pkill -SIGINT tshark")

def create_bg_node(net, i, prefix):
    return net.addDocker(f'bg_{prefix}_{i}', 
            ip=f'10.0.{prefix}.{i}', 
            dimage="test_client:latest",
            volumes={
                mounted_folder: {
                    "bind": "/mounted/", "mode":"rw"
            }})

def experiment():
    setLogLevel('info')
    
    # Initialize the Containernet instance
    net = Containernet(controller=Controller, switch=OVSSwitch, link=TCLink)
    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Adding switches\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')

    info('*** Adding hosts\n')

    client = net.addDocker('h1', 
            ip='10.0.0.1', 
            dimage="test_client:latest",
            volumes={
                mounted_folder: {
                    "bind": "/mounted/", "mode":"rw"
            }})


    server = net.addDocker('h2', 
            ip='10.0.0.2', 
            dimage="test_server:latest",
            volumes={
                mounted_folder: {
                    "bind": "/mounted/", "mode":"rw"
            }},
            dcmd="python3 -m http.server --directory /mounted/server/"
            )

    client_bg_nodes = [create_bg_node(net, i, 1) for i in range(1, 3)] 
    server_bg_nodes = [create_bg_node(net, i, 2) for i in range(1, 3)] 

    info('*** Adding links\n')
    # Connecting client to switch3
    net.addLink(client, s3, intfName1='h1-eth0', cls=TCLink, params1={'mtu': 1500})
    # Connecting server to switch1
    net.addLink(server, s1, intfName1='h2-eth0', cls=TCLink, params1={'mtu': 1500})
    # Connecting the main switches
    net.addLink(s1, s2, cls=TCLink, delay=f"10ms", bw=10)
    # Connecting switch2 to switch3
    bottleneck_link = net.addLink(s2, s3)

    # Connect the clients
    for n in client_bg_nodes:
        net.addLink(n, s2)
    for n in server_bg_nodes:
        net.addLink(n, s1)

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

    info('*** Starting IPerf\n')
    client_node = client_bg_nodes[0]
    server_node = server_bg_nodes[0]
    server_node.cmd("iperf -s &")
    client_node.cmd(f"iperf -c {server_node.IP()} -t 100 -u -b 10M &")
    info(f"set up pair on {client_node.name} - {server_node.name}\n")
    
    client_node = client_bg_nodes[0]
    server_node = server_bg_nodes[0]
    server_node.cmd("iperf -s &")
    client_node.cmd(f"iperf -c {server_node.IP()} -t 100 -b 5M &")
    info(f"set up pair on {client_node.name} - {server_node.name}\n")

    time.sleep(1)
    info('*** Testing capture\n')
    download_with_cap("shakespeare_1MB.txt", pcap_out_file, server, client)

    #info('*** Starting CLI\n')
    #CLI(net)

    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    experiment()
