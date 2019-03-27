#!/usr/bin/python

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import RemoteController, OVSSwitch
from ft4 import *
from trafficPatterns import *
from subprocess import Popen
from multiprocessing import Process
from mininet.link import TCLink,Link
from staticFlows import *
import time
import os

def fatTreeNet():
	topo=Fattree()
	topo.set_ovs_protocol_13()
	#net = Mininet(topo=topo, link=TCLink, switch=OVSSwitch, controller=RemoteController)
	net = Mininet(topo=topo, link=TCLink, switch=OVSSwitch, controller=None)
	flows=staticFlows()
	net.start()
	topo.set_ovs_protocol_13()
	flows.getFlows()
	CLI(net)

if __name__ == '__main__':
	setLogLevel('info')
	fatTreeNet()
	


