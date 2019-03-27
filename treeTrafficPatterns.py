#!/usr/bin/python

import random
import numpy


class TrafficPattern():
    def Random(self, hosts):

        pairs = []
        for host in hosts:
            pairs.append((host, random.choice([_ for _ in hosts if _ is not host])))
        return pairs


    def _Stride(self, hosts, i):
        pairs = []
        for index, host in enumerate(hosts):
            pairs.append((host, hosts[(index + i) % len(hosts)]))
        return pairs



    def Stride1(self, hosts):
        return self._Stride(hosts, 1)

    def Stride2(self, hosts):
        return self._Stride(hosts, 2)

    def Stride4(self, hosts):
        return self._Stride(hosts, 4)

    def Stride8(self, hosts):
        return self._Stride(hosts, 8)

    def _Staggered(self, hosts, subnet_p, pod_p):
        pairs = []
        for index, host in enumerate(hosts):
            toss = random.random()
            if toss <= subnet_p:
                pairs.append((host, hosts[index + 1 if index % 2 == 0 else index - 1]))
            elif toss <= subnet_p + pod_p:
                pod = index / 4
                party2 = random.randint(pod * 4, (pod + 1) * 4 - 1)
                while party2 == index:
                    party2 = random.randint(pod*4, (pod+1) * 4 - 1)
                pairs.append((host, hosts[party2]))
            else:
                pod = index / 4
                choices = list(range(0, pod*4)) + list(range((pod+1)*4, len(hosts)))
                pairs.append((host, hosts[random.choice(choices)]))
        return pairs

    def Staggered_1_0(self, hosts):
        return self._Staggered(hosts, 1, 0)


    def Staggered_05_03(self, hosts):
        return self._Staggered(hosts, 0.5, 0.3)


    def Staggered_02_03(self, hosts):
        return self._Staggered(hosts, 0.2, 0.3)



    def Interpod(self, hosts):
        chosen_pod = random.randint(0, 3)
        pairs= []
        for index, host in enumerate(hosts):
            party2 = random.randint(chosen_pod * 4, (chosen_pod + 1) * 4 - 1)
            while party2 == index:
                party2 = random.randint(chosen_pod * 4, (chosen_pod + 1) * 4 - 1)
            pairs.append((host, hosts[party2]))
        return pairs



    def SameID(self, hosts):
        pairs= []
        for index, host in enumerate(hosts):
            party2 = random.choice([(index + 4) % 16, (index + 8) % 16, (index + 12) % 16])
            pairs.append((host, hosts[party2]))
        return pairs



def srcDest(trafficMatrix, hosts):
    srcDst = []
    for i in range(len(trafficMatrix)):
        for j in range(len(trafficMatrix[i])):
            if (trafficMatrix[i][j] == 1):
                srcDst.append((hosts[i], hosts[j]))
    return srcDst



