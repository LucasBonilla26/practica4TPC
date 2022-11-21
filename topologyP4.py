from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import Host
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info

class LeafSpine( Topo ):
	def __init__( self ):
            # Initialize topology
            Topo.__init__( self )

            # Add hosts and switches
            host1 = self.addHost( 'h1' , ip='10.0.1.100/24',mac='00:00:00:00:00:01',defaultRoute="via 10.0.1.1")
            host2 = self.addHost('h2', ip='10.0.2.100/24',mac='00:00:00:00:00:02',defaultRoute="via 10.0.2.1")
            host3 = self.addHost('h3', ip='10.0.3.100/24',mac='00:00:00:00:00:03',defaultRoute="via 10.0.3.1")

            centralSwitch = self.addSwitch('s1')
            # Add links

            self.addLink( host1, centralSwitch )
            self.addLink( host2, centralSwitch )
            self.addLink( host3, centralSwitch )

topos = { 'mytopo': ( lambda: LeafSpine() ) }

