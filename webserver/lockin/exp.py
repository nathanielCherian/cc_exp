from mininet.net import Containernet
from mininet.node import Controller, OVSSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import time

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

def experiment():
    setLogLevel('info')
    
    # Initialize the Containernet instance
    net = Containernet(controller=Controller, switch=OVSSwitch, link=TCLink)
    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Adding switches\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')

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

    #client = net.addHost('h1', ip='10.0.0.1')
    #server = net.addHost('h2', ip='10.0.0.2')

    info('*** Adding links\n')
    # Connect client to switch 1 with MTU 1500
    net.addLink(client, s1, intfName1='h1-eth0', cls=TCLink, params1={'mtu': 1500})
    
    # Connect server to switch 2 with MTU 1500
    net.addLink(server, s2, intfName1='h2-eth0', cls=TCLink, params1={'mtu': 1500})
    
    info('*** Starting network\n')
    net.start()

    # Connect switch 1 and switch 2 with bottleneck settings
    bottleneck_link = net.addLink(s1, s2)
    s1_iface = bottleneck_link.intf1.name
    s2_iface = bottleneck_link.intf2.name

    # Configure the FIFO qdisc on the bottleneck link
    info('*** Configuring TC settings on bottleneck link\n')
    net.get('s1').cmd(f'tc qdisc add dev {s1_iface} root handle 1: netem delay 50ms')
    net.get('s1').cmd(f'tc qdisc add dev {s1_iface} parent 1:1 handle 10: tbf rate 200kbit burst 1540 limit 20000')
    #net.get('s1').cmd(f'tc qdisc add dev {s1_iface} parent 10: pfifo limit 10')
    net.get('s1').cmd(f'tc qdisc add dev {s1_iface} parent 10: bfifo limit 20000')

    net.get('s2').cmd(f'tc qdisc add dev {s2_iface} root handle 1: netem delay 50ms')
    net.get('s2').cmd(f'tc qdisc add dev {s2_iface} parent 1:1 handle 10: tbf rate 200kbit burst 1540 limit 20000')
    #net.get('s2').cmd(f'tc qdisc add dev {s2_iface} parent 10: pfifo limit 10')
    net.get('s2').cmd(f'tc qdisc add dev {s2_iface} parent 10: bfifo limit 20000')

    info('*** Verifying TC settings\n')
    info(net.get('s1').cmd(f'tc qdisc show dev {s1_iface}'))
    info(net.get('s2').cmd(f'tc qdisc show dev {s2_iface}'))
        

    info('*** Testing connectivity\n')
    net.pingAll()


    info('*** Testing capture\n')
    download_with_cap("shakespeare_1MB.txt", "test.pcap", server, client)

    info('*** Starting CLI\n')
    CLI(net)

    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    experiment()
