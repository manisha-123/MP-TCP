from mininet.topo import Topo
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import CPULimitedHost


class SingleSwitchTopo(Topo):
    "Single switch connected to n hosts."
    def build(self, n=2):
        switch = self.addSwitch('s1')
        # Python's range(N) generates 0..N-1
        for h in range(n):
            host = self.addHost('h%s' % (h + 1))
	    self.addLink(host, switch, bw=1000 )
            self.addLink(host, switch, bw=1000 )

   
def simpleTest():
    "Create and test a simple network"
    topo = SingleSwitchTopo(n=2)
    net = Mininet(topo = topo, link=TCLink)
    net.start()
    
    h1=net.get('h1')
    h1.cmd('ifconfig h1-eth0 10.0.0.50 netmask 255.0.0.0')
    h1.cmd('ifconfig h1-eth1 172.168.0.50 netmask 255.255.0.0') 

    h1.cmdPrint('ip rule add from 10.0.0.50 table 1')
    h1.cmdPrint('ip route add 10.0.0.0/8 dev h1-eth0 scope link table 1')
    h1.cmdPrint('ip route add default via 10.0.0.50 dev h1-eth0 table 1')
    h1.cmdPrint('ip route add default scope global nexthop via 10.0.0.50 dev h1-eth0')

    h1.cmdPrint('ip rule add from 172.168.0.50 table 2')
    h1.cmdPrint('ip route add 172.168.0.0/16 dev h1-eth1 scope link table 2')
    h1.cmdPrint('ip route add default via 172.168.0.50 dev h1-eth1 table 2')
    h1.cmdPrint('ip route add default scope global nexthop via 172.168.0.50 dev h1-eth1')
    


    h2=net.get('h2')
    h2.cmd('ifconfig h2-eth0 10.0.0.100 netmask 255.0.0.0')
    h2.cmd('ifconfig h2-eth1 172.168.0.100 netmask 255.255.0.0')

    h2.cmdPrint('ip rule add from 10.0.0.100 table 3')
    h2.cmdPrint('ip route add 10.0.0.0/8 dev h2-eth0 scope link table 3')
    h2.cmdPrint('ip route add default via 10.0.0.50 dev h2-eth0 table 3')
    h2.cmdPrint('ip route add default scope global nexthop via 10.0.0.50 dev h2-eth0')

    h2.cmdPrint('ip rule add from 172.168.0.100 table 4')
    h2.cmdPrint('ip route add 172.168.0.0/16 dev h2-eth1 scope link table 4')
    h2.cmdPrint('ip route add default via 172.168.0.50 dev h2-eth1 table 4')
    h2.cmdPrint('ip route add default scope global nexthop via 172.168.0.50 dev h2-eth1')
    
     

    print("Dumping host connections")
    dumpNodeConnections(net.hosts)
    print("Testing network connectivity")
    #	net.pingAll()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
