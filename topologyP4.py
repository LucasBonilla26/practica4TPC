from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import Host
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def topologyP4():
    "Create custom topo."
    # Initialize topology
    net = Mininet(topo=None, build=False, link=TCLink, controller=None)
    # Add hosts and switches
    Host1 = net.addHost( 'h1' , ip='10.0.1.100/24',mac='00:00:00:00:00:01',defaultRoute="via 10.0.1.1")
    Host2 = net.addHost('h2', ip='10.0.2.100/24',mac='00:00:00:00:00:02',defaultRoute="via 10.0.2.1")
    Host3 = net.addHost('h3', ip='10.0.3.100/24',mac='00:00:00:00:00:03',defaultRoute="via 10.0.3.1")

    centralSwitch = net.addSwitch('s1')
    # Add links
    
    net.addLink( Host1, centralSwitch )
    net.addLink( Host2, centralSwitch )
    net.addLink( Host3, centralSwitch )

    net.addLink(aloneHost7, centralSwitch)

    #Ejecución de la red
    net.start()

    CLI(net)

    net.stop()


if __name__ == "__main__":
    setLogLevel('info')
    topologyP4()

