#!/usr/bin/python

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import RemoteController, OVSSwitch
from mininet.util import irange, dumpNodeConnections
from mininet.link import TCLink


class DatacenterBasicTreeTopo(Topo):
    def __init__(self):
        Topo.__init__(self)

    def build(self):
        self.racks = []
        print "Creating root switch s1"
        rootSwitch = self.addSwitch('s1')
        for i in irange(1, 4):
            rack = self.buildRack(i)
            self.racks.append(rack)
            for switch in rack:
                print "Adding link between root switch s1 and switch s"
                self.addLink(rootSwitch, switch, bw=106.67)

    def buildRack(self, loc):
        "Build a rack of hosts with a top-of-rack switch"

        dpid = (loc * 16) + 1
        print "Creating lower switch s%s" % (int(loc) + 1)
        switch = self.addSwitch('s%s' % (int(loc) + 1), dpid='%x' % dpid)

        for n in irange(1, 4):
            host = self.addHost('h%s%s' % (n, loc))
            print "Adding link between host h%s%s and switch s%s" % (n, loc, int(loc) + 1)
            self.addLink(switch, host, bw=96)

        # Return list of top-of-rack switches for this rack
        return [switch]


# Allows the file to be imported using `mn --custom <filename> --topo dcbasic`
topos = {
    'dcTree': DatacenterBasicTreeTopo
}
