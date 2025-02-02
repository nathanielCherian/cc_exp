from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch
from mininet.link import TCLink
from mininet.cli import CLI

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

    print("*** Running CLI")
    CLI(net)

    print("*** Stopping Network")
    net.stop()

if __name__ == '__main__':
    custom_topology()
