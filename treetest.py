#!/usr/bin/python

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import RemoteController, OVSSwitch
from dcTree import DatacenterBasicTreeTopo
from treeTrafficPatterns import *
from subprocess import Popen
from multiprocessing import Process
from mininet.link import TCLink, Link
import time
import os


def treeNet():
    # Popen("cd ~/ryu/ryu && ryu-manager app/simple_switch_13.py ",shell=True)
    topo = DatacenterBasicTreeTopo()
    time.sleep(5)


    net = Mininet(topo=topo, link=TCLink, switch=OVSSwitch, controller=None)
    net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)  # ryu
    # net.addController('c0',controller=RemoteController, ip='127.0.0.1', port=6653)#floodlight
    # net = Mininet(topo=topo, link=TCLink, switch=OVSSwitch)
    return net


def Tests(net):
    net.start()
    net.pingAll()
    net.pingAll()
    net.pingAll()
    # CLI(net)
    hosts = getHostsTree()


    tp = TrafficPattern()
    srcDests=tp.Random(hosts)
    startServers(net, hosts, "random")
    print("Random")
    perfTests(net,srcDests,"random")

    srcDests=tp.Stride1(hosts)
    startServers(net,hosts,"stride1")
    print("Stride1")
    perfTests(net,srcDests,"stride1")

    srcDests=tp.Stride2(hosts)
    startServers(net,hosts,"stride2")
    print("Stride2")
    perfTests(net,srcDests,"stride2")

    srcDests=tp.Stride4(hosts)
    startServers(net,hosts,"stride4")
    print("Stride4")
    perfTests(net,srcDests,"stride4")

    srcDests = tp.Stride8(hosts)
    startServers(net, hosts, "stride8")
    print("Stride8")
    perfTests(net, srcDests, "stride8")


    srcDests=tp.Staggered_1_0(hosts)
    startServers(net,hosts,"Stag_1_0")
    print("Stag_1_0")
    perfTests(net,srcDests,"stag_1_0")

    srcDests=tp.Staggered_05_03(hosts)
    startServers(net,hosts,"Stag_5_3")
    print("Stag_5_3")
    perfTests(net,srcDests,"stag_5_3")

    srcDests=tp.Staggered_02_03(hosts)
    startServers(net,hosts,"Stag_2_3")
    print("Stag_2_3")
    perfTests(net,srcDests,"stag_2_3")

    srcDests=tp.Interpod(hosts)
    startServers(net,hosts,"InterPod")
    print("InterPod")
    perfTests(net,srcDests,"interPod")

    srcDests=tp.SameID(hosts)
    startServers(net,hosts,"SameID")
    print("SameID")
    perfTests(net,srcDests,"SameID")


def getHostsTree():
    hosts = []
    for i in range(1, 5, 1):
        for j in range(1, 5, 1):
            hosts.append("h" + str(j) + str(i))
    for h in hosts:
        print(h)
    return hosts



def startServers(net, hosts, pattern):

    for host in hosts:

        h = net.get(host)
        file_name_bw = 'treeResultsBW/source_{}_{}.txt'.format(pattern, h)
        h.cmd("iperf -s > %s &" % (file_name_bw))


def perfTests(net, srcDests, pattern):

    for [src, dest] in srcDests:
        s = net.get(src)
        d = net.get(dest)
        print(s,d)
        file_name_bw = 'treeResultsBW/{}_{}.txt'.format(pattern, src)
        s.cmd("iperf -c %s -t %d -f m > %s  &" % (d.IP(), 100, file_name_bw))
        time.sleep(2)

    # Wait for the traffic to become stable.
    time.sleep(30)
    file_name_bwmng = 'treeResultsBW/bwmng_{}.txt'.format(pattern)
    os.system('touch %s' % file_name_bwmng)
    f = open(file_name_bwmng, 'a+')  # open file in append mode
    f.close()

    #  Start bwm-ng
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
    net = treeNet()
    Tests(net)
    net.stop()
    # clean up.
    os.system('mn -c')
