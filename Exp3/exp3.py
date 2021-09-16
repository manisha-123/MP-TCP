#!/usr/bin/python

import os
import sys
from subprocess import Popen, PIPE
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from time import sleep
import termcolor as T
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.log import lg
from mininet.topo import SingleSwitchTopo
from mininet.cli import CLI

class SingleSwitchTopo(Topo):
    "Single switch connected to n hosts."

    def build(self, n=2):
        switch = self.addSwitch('s1')
        for h in range(5):
            host = self.addHost('h%s' % (h + 1))
            self.addLink(host, switch, bw=1000)
            self.addLink(host, switch, bw=1000)
            if h == 0:
                self.addLink(host, switch, bw=1000)
                self.addLink(host, switch, bw=1000)


def progress(t):
    while t > 0:
        print T.colored('  %3d seconds left  \r' % (t), 'cyan'),
        t -= 1
        sys.stdout.flush()
        sleep(1)
    print '\r\n'

def routeConfig(h):
    for i in range(1,6):
        lg.info("configuring source-specific routing tables for MPTCP\n")
    
        j = i-1
        dev = 'h%i-eth0' % i
        h[j].cmdPrint('ip rule add from 10.0.0.%i table 1' % i)
        h[j].cmdPrint('ip route add 10.0.0.0/8 dev %s scope link table 1' % dev)
        h[j].cmdPrint('ip route add default via 10.0.0.1 dev %s table 1' % dev)
    
        dev = 'h%i-eth1' % i
        h[j].cmdPrint('ip rule add from 172.168.0.%i table 2' % i)
        h[j].cmdPrint('ip route add 172.168.0.0/18 dev %s scope link table 2' % dev)
        h[j].cmdPrint('ip route add default via 172.168.0.1 dev %s table 2' % dev)

    h[0].cmdPrint('ip rule add from 172.168.64.1 table 3')
    h[0].cmdPrint('ip route add 172.168.64.0/18 dev h1-eth2 scope link table 3')
    h[0].cmdPrint('ip route add default via 172.168.64.1 dev h1-eth2 table 3')

    h[0].cmdPrint('ip rule add from 172.168.128.1 table 4')
    h[0].cmdPrint('ip route add 172.168.128.0/18 dev h1-eth3 scope link table 4')
    h[0].cmdPrint('ip route add default via 172.168.128.1 dev h1-eth3 table 4')

def sysctl_set(key, value):
    """Issue systcl for given param to given value and check for error."""
    p = Popen("sysctl -w %s=%s" % (key, value), shell=True, stdout=PIPE,
              stderr=PIPE) 
    stdout, stderr = p.communicate()
    stdout_expected = "%s = %s\n" % (key, value)
    if stdout != stdout_expected:
        raise Exception("Popen returned unexpected stdout: %s != %s" %
                        (stdout, stdout_expected))
    if stderr:
        raise Exception("Popen returned unexpected stderr: %s" % stderr)


def set_mptcp_enabled(enabled):
    """Enable MPTCP if true, disable if false"""
    e = 1 if enabled else 0
    lg.info("setting MPTCP enabled to %s\n" % e)
    sysctl_set('net.mptcp.mptcp_enabled', e)


def iperfLaunch(h):
    lg.info("iperfing")
    sleep(1)
    seconds=320
    for i in range(1,4):
        cmd = 'iperf -c %s -p 500%i -n 4096M -i 1 &' % (h[0].IP(), i)
        h[i].cmd(cmd)
    return None

def simpleTest():
    "Configure interfaces"
    topo = SingleSwitchTopo(n=4)
    net = Mininet(topo, link=TCLink)
    net.start()
    h1, h2, h3, h4, h5 = net.hosts
    h1.cmd('ifconfig h1-eth1 172.168.0.1 netmask 255.255.192.0')
    h2.cmd('ifconfig h2-eth1 172.168.0.2 netmask 255.255.192.0')
    h2.cmd('ifconfig h2-eth0:1 172.168.64.4 netmask 255.255.192.0')
    h2.cmd('ifconfig h2-eth0:2 172.168.64.7 netmask 255.255.192.0')
    h2.cmd('ifconfig h2-eth1:1 172.168.128.7 netmask 255.255.192.0')
    h2.cmd('ifconfig h2-eth1:2 172.168.128.4 netmask 255.255.192.0')
    h3.cmd('ifconfig h3-eth1 172.168.0.3 netmask 255.255.192.0')
    h3.cmd('ifconfig h3-eth0:1 172.168.64.5 netmask 255.255.192.0')
    h3.cmd('ifconfig h3-eth0:2 172.168.64.8 netmask 255.255.192.0')
    h3.cmd('ifconfig h3-eth1:1 172.168.128.8 netmask 255.255.192.0')
    h3.cmd('ifconfig h3-eth1:2 172.168.128.5 netmask 255.255.192.0')
    h4.cmd('ifconfig h4-eth1 172.168.0.4 netmask 255.255.192.0')
    h4.cmd('ifconfig h4-eth0:1 172.168.64.6 netmask 255.255.192.0')
    h4.cmd('ifconfig h4-eth0:2 172.168.64.9 netmask 255.255.192.0')
    h4.cmd('ifconfig h4-eth1:1 172.168.128.9 netmask 255.255.192.0')
    h4.cmd('ifconfig h4-eth1:2 172.168.128.6 netmask 255.255.192.0')
    h5.cmd('ifconfig h5-eth1 172.168.0.5 netmask 255.255.192.0')
    h5.cmd('ifconfig h5-eth0:1 172.168.64.2 netmask 255.255.192.0')
    h5.cmd('ifconfig h5-eth0:2 172.168.64.10 netmask 255.255.192.0')
    h5.cmd('ifconfig h5-eth1:1 172.168.128.10 netmask 255.255.192.0')
    h5.cmd('ifconfig h5-eth1:2 172.168.128.2 netmask 255.255.192.0')
    h1.cmd('ifconfig h1-eth2 172.168.64.1 netmask 255.255.192.0')
    h1.cmd('ifconfig h1-eth3 172.168.128.1 netmask 255.255.192.0')

    dumpNodeConnections(net.hosts)
    net.pingAll()
    set_mptcp_enabled(True)
    routeConfig(net.hosts)
    h1.cmd('iperf -s -p 5001 -i 1 &')
    h1.cmd('iperf -s -p 5002 -i 1 &')
    h1.cmd('iperf -s -p 5003 -i 1 &')
    h1.cmd('iperf -s -p 5004 -i 1 &')
    h1.cmd('iperf -s -p 5000 -i 1 &')
    iperfLaunch(net.hosts)
    print "\nh5 iperf -c h1 -p 5004 -n 1024M -i 1"
    CLI(net)
    net.stop()
    os.system("sudo mn -c")


if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
