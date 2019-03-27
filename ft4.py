#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import Link, Intf, TCLink
from mininet.topo import Topo
from mininet.util import dumpNodeConnections
from treeTrafficPatterns import *
import logging
import os
from subprocess import Popen
from multiprocessing import Process
import time
class Fattree(Topo):
    """
        Class of Fattree Topology.
    """
    CoreSwitchList = []
    AggSwitchList = []
    EdgeSwitchList = []
    HostList = []

    def __init__(self, k, density):
        self.pod = k
        self.density = density
        self.iCoreLayerSwitch = (k / 2) ** 2
        self.iAggLayerSwitch = k * k / 2
        self.iEdgeLayerSwitch = k * k / 2
        self.iHost = self.iEdgeLayerSwitch * density

        # Init Topo
        Topo.__init__(self)

    def createNodes(self):
        self.createCoreLayerSwitch(self.iCoreLayerSwitch)
        self.createAggLayerSwitch(self.iAggLayerSwitch)
        self.createEdgeLayerSwitch(self.iEdgeLayerSwitch)
        self.createHost(self.iHost)

    # Create Switch and Host
    def _addSwitch(self, number, level, switch_list):
        """
            Create switches.
        """
        for i in xrange(1, number + 1):
            PREFIX = str(level) + "00"
            if i >= 10:
                PREFIX = str(level) + "0"
            switch_list.append(self.addSwitch(PREFIX + str(i)))

    def createCoreLayerSwitch(self, NUMBER):
        self._addSwitch(NUMBER, 1, self.CoreSwitchList)

    def createAggLayerSwitch(self, NUMBER):
        self._addSwitch(NUMBER, 2, self.AggSwitchList)

    def createEdgeLayerSwitch(self, NUMBER):
        self._addSwitch(NUMBER, 3, self.EdgeSwitchList)

    def createHost(self, NUMBER):
        """
            Create hosts.
        """
        for i in xrange(1, NUMBER + 1):
            if i >= 100:
                PREFIX = "h"
            elif i >= 10:
                PREFIX = "h0"
            else:
                PREFIX = "h00"
            self.HostList.append(self.addHost(PREFIX + str(i), cpu=1.0 / NUMBER))

    def createLinks(self, bw_c2a=10, bw_a2e=10, bw_e2h=10):
        """
            Add network links.
        """
        # Core to Agg
        end = self.pod / 2
        for x in xrange(0, self.iAggLayerSwitch, end):
            for i in xrange(0, end):
                for j in xrange(0, end):
                    self.addLink(
                        self.CoreSwitchList[i * end + j],
                        self.AggSwitchList[x + i],
                        bw=bw_c2a, max_queue_size=1000)  # use_htb=False

        # Agg to Edge
        for x in xrange(0, self.iAggLayerSwitch, end):
            for i in xrange(0, end):
                for j in xrange(0, end):
                    self.addLink(
                        self.AggSwitchList[x + i], self.EdgeSwitchList[x + j],
                        bw=bw_a2e, max_queue_size=1000)  # use_htb=False

        # Edge to Host
        for x in xrange(0, self.iEdgeLayerSwitch):
            for i in xrange(0, self.density):
                self.addLink(
                    self.EdgeSwitchList[x],
                    self.HostList[self.density * x + i],
                    bw=bw_e2h, max_queue_size=1000)  # use_htb=False

    def set_ovs_protocol_13(self, ):
        """
            Set the OpenFlow version for switches.
        """
        self._set_ovs_protocol_13(self.CoreSwitchList)
        self._set_ovs_protocol_13(self.AggSwitchList)
        self._set_ovs_protocol_13(self.EdgeSwitchList)

    def _set_ovs_protocol_13(self, sw_list):
        for sw in sw_list:
            cmd = "sudo ovs-vsctl set bridge %s protocols=OpenFlow13" % sw
            os.system(cmd)


def set_host_ip(net, topo):
    hostlist = []
    for k in xrange(len(topo.HostList)):
        hostlist.append(net.get(topo.HostList[k]))
    i = 1
    j = 1
    for host in hostlist:
        host.setIP("10.%d.0.%d" % (i, j))
        j += 1
        if j == topo.density + 1:
            j = 1
            i += 1


def create_subnetList(topo, num):
    """
        Create the subnet list of the certain Pod.
    """
    subnetList = []
    remainder = num % (topo.pod / 2)
    if topo.pod == 4:
        if remainder == 0:
            subnetList = [num - 1, num]
        elif remainder == 1:
            subnetList = [num, num + 1]
        else:
            pass
    elif topo.pod == 8:
        if remainder == 0:
            subnetList = [num - 3, num - 2, num - 1, num]
        elif remainder == 1:
            subnetList = [num, num + 1, num + 2, num + 3]
        elif remainder == 2:
            subnetList = [num - 1, num, num + 1, num + 2]
        elif remainder == 3:
            subnetList = [num - 2, num - 1, num, num + 1]
        else:
            pass
    else:
        pass
    return subnetList


def install_proactive(net, topo):
    """
        Install proactive flow entries for switches.
    """
    # Edge Switch
    for sw in topo.EdgeSwitchList:
        num = int(sw[-2:])

        # Downstream.
        for i in xrange(1, topo.density + 1):
            cmd = "ovs-ofctl add-flow %s -O OpenFlow13 \
				'table=0,idle_timeout=0,hard_timeout=0,priority=40,arp, \
				nw_dst=10.%d.0.%d,actions=output:%d'" % (sw, num, i, topo.pod / 2 + i)
            os.system(cmd)
            cmd = "ovs-ofctl add-flow %s -O OpenFlow13 \
				'table=0,idle_timeout=0,hard_timeout=0,priority=40,ip, \
				nw_dst=10.%d.0.%d,actions=output:%d'" % (sw, num, i, topo.pod / 2 + i)
            os.system(cmd)

        # Upstream.
        if topo.pod == 4:
            cmd = "ovs-ofctl add-group %s -O OpenFlow13 \
			'group_id=1,type=select,bucket=output:1,bucket=output:2'" % sw
        elif topo.pod == 8:
            cmd = "ovs-ofctl add-group %s -O OpenFlow13 \
			'group_id=1,type=select,bucket=output:1,bucket=output:2,\
			bucket=output:3,bucket=output:4'" % sw
        else:
            pass
        os.system(cmd)
        cmd = "ovs-ofctl add-flow %s -O OpenFlow13 \
		'table=0,priority=10,arp,actions=group:1'" % sw
        os.system(cmd)
        cmd = "ovs-ofctl add-flow %s -O OpenFlow13 \
		'table=0,priority=10,ip,actions=group:1'" % sw
        os.system(cmd)

    # Aggregate Switch
    for sw in topo.AggSwitchList:
        num = int(sw[-2:])
        subnetList = create_subnetList(topo, num)

        # Downstream.
        k = 1
        for i in subnetList:
            cmd = "ovs-ofctl add-flow %s -O OpenFlow13 \
				'table=0,idle_timeout=0,hard_timeout=0,priority=40,arp, \
				nw_dst=10.%d.0.0/16, actions=output:%d'" % (sw, i, topo.pod / 2 + k)
            os.system(cmd)
            cmd = "ovs-ofctl add-flow %s -O OpenFlow13 \
				'table=0,idle_timeout=0,hard_timeout=0,priority=40,ip, \
				nw_dst=10.%d.0.0/16, actions=output:%d'" % (sw, i, topo.pod / 2 + k)
            os.system(cmd)
            k += 1

        # Upstream.
        if topo.pod == 4:
            cmd = "ovs-ofctl add-group %s -O OpenFlow13 \
			'group_id=1,type=select,bucket=output:1,bucket=output:2'" % sw
        elif topo.pod == 8:
            cmd = "ovs-ofctl add-group %s -O OpenFlow13 \
			'group_id=1,type=select,bucket=output:1,bucket=output:2,\
			bucket=output:3,bucket=output:4'" % sw
        else:
            pass
        os.system(cmd)
        cmd = "ovs-ofctl add-flow %s -O OpenFlow13 \
		'table=0,priority=10,arp,actions=group:1'" % sw
        os.system(cmd)
        cmd = "ovs-ofctl add-flow %s -O OpenFlow13 \
		'table=0,priority=10,ip,actions=group:1'" % sw
        os.system(cmd)

    # Core Switch
    for sw in topo.CoreSwitchList:
        j = 1
        k = 1
        for i in xrange(1, len(topo.EdgeSwitchList) + 1):
            cmd = "ovs-ofctl add-flow %s -O OpenFlow13 \
				'table=0,idle_timeout=0,hard_timeout=0,priority=10,arp, \
				nw_dst=10.%d.0.0/16, actions=output:%d'" % (sw, i, j)
            os.system(cmd)
            cmd = "ovs-ofctl add-flow %s -O OpenFlow13 \
				'table=0,idle_timeout=0,hard_timeout=0,priority=10,ip, \
				nw_dst=10.%d.0.0/16, actions=output:%d'" % (sw, i, j)
            os.system(cmd)
            k += 1
            if k == topo.pod / 2 + 1:
                j += 1
                k = 1


def pingTest(net):
    """
        Start ping test.
    """
    net.pingAll()


def getHostsFatTree():
    hosts = []
    for i in xrange(1, 17):
        if i >= 100:
            PREFIX = "h"
        elif i >= 10:
            PREFIX = "h0"
        else:
            PREFIX = "h00"
        hosts.append(PREFIX + str(i))
    return hosts


def createTopo(pod=4, density=2, ip="192.168.56.101", port=6653, bw_c2a=96, bw_a2e=96, bw_e2h=96):
    """
        Create network topology and run the Mininet.
    """
    # Create Topo.
    topo = Fattree(pod, density)
    topo.createNodes()
    topo.createLinks(bw_c2a=bw_c2a, bw_a2e=bw_a2e, bw_e2h=bw_e2h)

    # Start Mininet.
    CONTROLLER_IP = ip
    CONTROLLER_PORT = port
    net = Mininet(topo=topo, link=TCLink, controller=None, autoSetMacs=True)
    # net.addController('controller', controller=RemoteController,ip=CONTROLLER_IP, port=CONTROLLER_PORT)
    net.start()

    # Set OVS's protocol as OF13.
    topo.set_ovs_protocol_13()
    # Set hosts IP addresses.
    set_host_ip(net, topo)
    # Install proactive flow entries
    install_proactive(net, topo)
    # dumpNodeConnections(net.hosts)
    # pingTest(net)
    # iperfTest(net, topo)

    # CLI(net)
    # net.stop()
    net.pingAll()
    net.pingAll()
    net.pingAll()
    # CLI(net)
    hosts = getHostsFatTree()

    tp = TrafficPattern()

    # srcDests=tp.Random(hosts)
    # startServers(net, hosts, "random")
    # print("Random")
    # perfTests(net,srcDests,"random")
    #
    # srcDests=tp.Stride1(hosts)
    # print("Stride 1")
    # startServers(net,hosts,"stride1")
    # perfTests(net,srcDests,"stride1")
    #
    # srcDests=tp.Stride2(hosts)
    # print("Stride 2")
    # startServers(net,hosts,"stride2")
    # perfTests(net,srcDests,"stride2")

    srcDests = tp.Stride4(hosts)
    print("Stride 4")
    startServers(net, hosts, "stride4")
    perfTests(net, srcDests, "stride4")


    # srcDests=tp.Stride8(hosts)
    # print("Stride 8")
    # startServers(net,hosts,"stride8")
    # perfTests(net,srcDests,"stride8")
    #
    # srcDests=tp.Staggered_1_0(hosts)
    # print("Staggered 1")
    # startServers(net,hosts,"stag_1_0")
    # perfTests(net,srcDests,"stag_1_0")
    #
    # srcDests=tp.Staggered_05_03(hosts)
    # print("Staggered_05_03")
    # startServers(net,hosts,"stag_5_3")
    # perfTests(net,srcDests,"stag_5_3")
    #
    # srcDests=tp.Staggered_02_03(hosts)
    # print("Staggered 2_3")
    # startServers(net,hosts,"stag_2_3")
    # perfTests(net,srcDests,"stag_2_3")
    #
    # srcDests=tp.Interpod(hosts)
    # print("Inter_pod")
    # startServers(net,hosts,"interPod")
    # perfTests(net,srcDests,"interPod")
    #
    # srcDests=tp.SameID(hosts)
    # print("SameID")
    # startServers(net,hosts,"SameID")
    # perfTests(net,srcDests,"SameID")
    net.stop()

def startServers(net, hosts, pattern):
    for host in hosts:
        h = net.get(host)
        file_name_bw = 'fatTreeResultsBW/source_{}_{}.txt'.format(pattern, h)
        h.cmd("iperf -s > %s &" % file_name_bw)


def perfTests(net, srcDests, pattern):
    for [src, dest] in srcDests:
        s = net.get(src)
        d = net.get(dest)
        print(src, dest)
        file_name_bw = 'fatTreeResultsBW/{}_{}.txt'.format(pattern, src)
        s.cmd("iperf -c %s -t %d -f m > %s &" % (d.IP(), 100, file_name_bw))
        time.sleep(2)

    # Wait for the traffic to become stable.
    time.sleep(30)
    file_name_bwmng = 'fatTreeResultsBW/bwmng_{}.txt'.format(pattern)
    os.system('touch %s' % file_name_bwmng)
    f = open(file_name_bwmng, 'a+')  # open file in append mode
    f.close()

    #  Start bwm-ng to monitor throughput.
    monitor = Process(target=monitor_devs_ng, args=(file_name_bwmng, 1.0))
    monitor.start()

    # The experiment is going on.
    time.sleep(100)

    # Shut down.
    monitor.terminate()
    os.system('killall bwm-ng')

    os.system('killall iperf')


def monitor_devs_ng(fname, interval_sec=0.01):
    cmd = "sleep 1; bwm-ng -t %s -o csv -u bits -T rate -C ',' > %s" % (interval_sec * 1000, fname)
    Popen(cmd, shell=True).wait()


if __name__ == '__main__':
    setLogLevel('info')
    if os.getuid() != 0:
        logging.debug("You are NOT root")
    elif os.getuid() == 0:
        createTopo(4, 2)
    # createTopo(8, 4)
