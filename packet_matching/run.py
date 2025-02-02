from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch
from mininet.link import TCLink
from mininet.cli import CLI
import time


def configure_bottleneck(bottleneck_link):
    print('*** Configuring TC settings on bottleneck link\n')
    n1, n2 = bottleneck_link.intf1.node, bottleneck_link.intf2.node
    n1_intf, n2_intf = bottleneck_link.intf1.name, bottleneck_link.intf2.name
    n1.cmd('tc qdisc add dev %s root handle 1: netem delay 50ms' % n1_intf)
    n1.cmd('tc qdisc add dev %s parent 1:1 handle 10: tbf rate 200kbit burst 1540 limit 20000' % n1_intf)
    n1.cmd('tc qdisc add dev %s parent 10: bfifo limit 20000' % n1_intf)

    n2.cmd('tc qdisc add dev %s root handle 1: netem delay 50ms' % n2_intf)
    n2.cmd('tc qdisc add dev %s parent 1:1 handle 10: tbf rate 200kbit burst 1540 limit 20000' % n2_intf)
    n2.cmd('tc qdisc add dev %s parent 10: bfifo limit 20000' % n2_intf)
    
    #print(bottleneck_link.intf1.node)
    #print(bottleneck_link.intf2.node)

def custom_topology():
    net = Mininet(controller=Controller, switch=OVSKernelSwitch, link=TCLink)

    print("*** Adding Controller")
    net.addController('c0')

    print("*** Adding Hosts")
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')

    print("*** Adding Switches")
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')

    print("*** Creating Links and Setting MAC Addresses")
    # h1 <--> s1
    link1 = net.addLink(h1, s1)
    h1.setMAC('00:00:00:00:01:01', intf=link1.intf1.name)
    s1.setMAC('00:00:00:00:01:02', intf=link1.intf2.name)

    # s1 <--> s2
    link2 = net.addLink(s1, s2)
    s1.setMAC('00:00:00:00:02:01', intf=link2.intf1.name)
    s2.setMAC('00:00:00:00:02:02', intf=link2.intf2.name)

    # s2 <--> h2
    link3 = net.addLink(s2, h2)
    s2.setMAC('00:00:00:00:03:01', intf=link3.intf1.name)
    h2.setMAC('00:00:00:00:03:02', intf=link3.intf2.name)

    print("*** Starting Network")
    net.start()

    # Setting the MTU
    for host in net.hosts + net.switches:
        for intf in host.intfs.values():
            if intf.name == "lo":
                continue
            print(intf.name)
            host.cmd("ip link set %s mtu 1500" % intf.name)
            #host.cmd("ethtool -K %s tso off gso off" % intf.name)

    configure_bottleneck(link2)

    print("starting tshark...")
    s1.cmd("tshark -i s1-eth1 -w pcaps/eth1.pcap &")
    s2.cmd("tshark -i s2-eth2 -w pcaps/eth2.pcap &")
    
    print("starting server...")
    h2.cmd("python3 -m http.server &")
    time.sleep(1)
    print("starting curl")
    h1.cmd("curl 10.0.0.2:8000/datafiles/file_1MB.txt > /dev/null")
    print("done curl")
    time.sleep(0.5)

    #print("*** Running CLI")
    #CLI(net)

    print("*** Stopping Network")
    net.stop()

if __name__ == '__main__':
    custom_topology()
