#!/usr/bin/python

class ecmpPaths():

	def getPath(self,srcIP,destIP):

		k=4
		paths=[]
		#src[10,pod,switch.id]
		src=srcIP.split(".")
		dst=destIP.split(".")
		#choose edge(1 choice only)
		edgeSrc=src[1]+"_"+src[2]+"_1"
		edgeDst=dst[1]+"_"+dst[2]+"_1"
		if (src[1]!=dst[1]):
			for i in range(k/2 , k):			
				#choose aggr(2 choices)
				aggrSrc=src[1]+"_"+str(i)+"_1"
				aggrDst=dst[1]+"_"+str(i)+"_1"
				for j in range(0 , k/2):
					path=[]
					num=(i % (k/2+1))
					core=str(4)+"_"+str(num)+"_"+str(j+1)
					path.append(srcIP)
					path.append(edgeSrc)
					path.append(aggrSrc)
					path.append(core)
					path.append(aggrDst)
					path.append(edgeDst)
					path.append(destIP)
					paths.append(path)
				
		else:
			if src[2]!=dst[2]:
				for i in range(k/2 , k):
					path=[]
					aggr=src[1]+"_"+str(i)+"_1"
					path.append(srcIP)
					path.append(edgeSrc)
					path.append(aggr)
					path.append(edgeDst)
					path.append(destIP)
					paths.append(path)
	
			else:
				path=[]
				path.append(srcIP)
				path.append(edgeSrc)
				path.append(destIP)
				paths.append(path)
		return paths


