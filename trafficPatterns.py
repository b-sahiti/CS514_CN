#!/usr/bin/python

import random
import numpy


class TrafficPattern():
    def Random(self, hosts):

        pairs = []
        for host in hosts:
            pairs.append((host, random.choice([_ for _ in hosts if _ is not host])))
        return pairs

    # hostCount=len(hosts)
    # trafficMatrix=[[0 for i in range(hostCount)]for j in range(hostCount)]
    # for i in range(hostCount):
    # 	for j in range(hostCount):
    # 		p=random.randint(1,11)
    # 		if(p>5):
    # 			trafficMatrix[i][j]=1
    # return srcDest(trafficMatrix,hosts)

    def _Stride(self, hosts, i):
        pairs = []
        for index, host in enumerate(hosts):
            pairs.append((host, hosts[(index + i) % len(hosts)]))
        return pairs

        # hostCount = len(hosts)
        # trafficMatrix = [[0 for i in range(hostCount)] for j in range(hostCount)]
        # # print(numpy.shape(trafficMatrix))
        # for i in range(hostCount):
        #     j = (i + i) % hostCount
        #     print(i, j)
        #     trafficMatrix[i][j] = 1
        # return srcDest(trafficMatrix, hosts)

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
        # hostCount = len(hosts)
        # trafficMatrix = [[0 for i in range(hostCount)] for j in range(hostCount)]
        # for i in range(hostCount):
        #     for j in range(hostCount):
        #         if ((i != j) and (i / 2 == j / 2)):
        #             trafficMatrix[i][j] = 1
        #         elif ((i != j) and (i / 4 == j / 4)):
        #             trafficMatrix[i][j] = 0
        #         elif ((i != j)):
        #             trafficMatrix[i][j] = 0
        # return srcDest(trafficMatrix, hosts)

    def Staggered_05_03(self, hosts):
        return self._Staggered(hosts, 0.5, 0.3)
        #
        # hostCount = len(hosts)
        # trafficMatrix = [[0 for i in range(hostCount)] for j in range(hostCount)]
        # for i in range(hostCount):
        #     for j in range(hostCount):
        #
        #         if ((i != j) and (i / 2 == j / 2)):
        #             p = random.random()
        #             if (p <= 0.5):
        #                 trafficMatrix[i][j] = 1
        #         elif ((i != j) and (i / 4 == j / 4)):
        #             p = random.random()
        #             if (p <= 0.3):
        #                 trafficMatrix[i][j] = 1
        #         elif ((i != j)):
        #             p = random.random()
        #             if (p <= 0.2):
        #                 trafficMatrix[i][j] = 1
        # return srcDest(trafficMatrix, hosts)

    def Staggered_02_03(self, hosts):
        return self._Staggered(hosts, 0.2, 0.3)

        #
        # hostCount = len(hosts)
        # trafficMatrix = [[0 for i in range(hostCount)] for j in range(hostCount)]
        # for i in range(hostCount):
        #     for j in range(hostCount):
        #         if ((i != j) and (i / 2 == j / 2)):
        #             p = random.random()
        #             if (p <= 0.2):
        #                 trafficMatrix[i][j] = 1
        #         elif ((i != j) and (i / 4 == j / 4)):
        #             p = random.random()
        #             if (p <= 0.3):
        #                 trafficMatrix[i][j] = 1
        #         elif (i != j):
        #             p = random.random()
        #             if (p <= 0.5):
        #                 trafficMatrix[i][j] = 1
        # return srcDest(trafficMatrix, hosts)

    def Interpod(self, hosts):
        chosen_pod = random.randint(0, 3)
        pairs= []
        for index, host in enumerate(hosts):
            party2 = random.randint(chosen_pod * 4, (chosen_pod + 1) * 4 - 1)
            while party2 == index:
                party2 = random.randint(chosen_pod * 4, (chosen_pod + 1) * 4 - 1)
            pairs.append((host, hosts[party2]))
        return pairs

        # hostCount = len(hosts)
        # trafficMatrix = [[0 for i in range(hostCount)] for j in range(hostCount)]
        # for i in range(hostCount):
        #     for j in range(hostCount):
        #         if (i / 4 != j / 4):
        #             trafficMatrix[i][j] = 1
        # return srcDest(trafficMatrix, hosts)

    def SameID(self, hosts):
        pairs= []
        for index, host in enumerate(hosts):
            party2 = random.choice([(index + 4) % 16, (index + 8) % 16, (index + 12) % 16])
            pairs.append((host, hosts[party2]))
        return pairs
        # hostCount = len(hosts)
        # trafficMatrix = [[0 for i in range(hostCount)] for j in range(hostCount)]
        # for i in range(hostCount):
        #     for j in range(hostCount):
        #         if ((i > j) and ((i / 2 - j / 2) % 2) == 0):
        #             trafficMatrix[i][j] = 1
        #         elif ((j > i) and ((j / 2 - i / 2) % 2) == 0):
        #             trafficMatrix[i][j] = 1
        # return srcDest(trafficMatrix, hosts)


def srcDest(trafficMatrix, hosts):
    srcDst = []

    # hosts=[h11,h12,h13,h14,h21,h22,h23,h24,h31,h32,h33,h34,h41,h42,h43,h44]
    for i in range(len(trafficMatrix)):
        for j in range(len(trafficMatrix[i])):
            if (trafficMatrix[i][j] == 1):
                srcDst.append((hosts[i], hosts[j]))
    return srcDst


if __name__ == '__main__':
    t = TrafficPattern()
    hosts = ["h11", "h12", "h13", "h14", "h21", "h22", "h23", "h24", "h31", "h32", "h33", "h34", "h41", "h42", "h43",
             "h44"]
    t.SameID(hosts)
