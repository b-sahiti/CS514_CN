#!/usr/bin/python

import random
import os

# open flow default add flow priority =32768
# priority range is 0 to 65535
class  staticFlows():
	def getFlows(self):
		k=4
		#edge switch flows -prefix-down flow, suffix - up flow
		#cmds=[]
		for p in range(0,k):
			for es in range(0,k/2):
				switch=str(p)+"_"+str(es)+"_"+str(1)
				#cmd = "sudo ovs-vsctl set bridge %s protocols=OpenFlow13" % switch
				#os.system(cmd)
				for h in range(2,k/2+2):					
					prefixIP=str(10)+"."+str(p)+"."+str(es)+"."+str(h)
					preficPort=h-1
					PrefixPriority=32768
					#suffixIP="0.0.0."+str(h)+"/"+str(8)
					suffixPort=((h-2+es) % (k/2))+(k/2)+1
					rand=100#random.randint(1,100)
					suffixPriority=rand
					# DOWN
					cmd="ovs-ofctl add-flow %s -O OpenFlow13 'table=0, idle_timeout=0,hard_timeout=0,priority=%s,arp,nw_dst=%s,actions=output:%s'" %(switch,PrefixPriority,prefixIP,preficPort)
					os.system(cmd)
					cmd="sudo ovs-ofctl add-flow %s -O OpenFlow13  'table=0, idle_timeout=0,hard_timeout=0,priority=%s,ip,nw_dst=%s,actions=output:%s'" %  (switch,PrefixPriority,prefixIP,preficPort)
					os.system(cmd)
					#UP
				cmd="ovs-ofctl add-group %s -O OpenFlow13 'group_id=5,type=select,bucket=output:%s,bucket=output:%s'" %(switch,3,4)
				os.system(cmd)
				cmd="ovs-ofctl add-flow %s -O OpenFlow13 'table=0,priority=100,arp,actions=group:5'"%(switch)
				os.system(cmd)
				cmd="ovs-ofctl add-flow %s -O OpenFlow13 'table=0,priority=100,ip,actions=group:5'"%(switch)
				os.system(cmd)

					
					

		for p in range(0,k):
			#aggregate switch flows prefix-down flow, suffix - up flow
			for ags in range(k/2,k):
				switch=	str(p)+"_"+str(ags)+"_"+str(1)
				#cmd = "sudo ovs-vsctl set bridge %s protocols=OpenFlow13" % switch
				#os.system(cmd)				
				for es in range(0,k/2):	
								
					prefixIP=str(10)+"."+str(p)+"."+str(es)+"."+str(0)+"/"+str(24)
					preficPort=es+1
					PrefixPriority=	32768
					#cmds.append(str("prefix =="+switch+","+prefixIP+","+str(preficPort)))
					cmd='ovs-ofctl add-flow %s -O OpenFlow13 "table=0, idle_timeout=0,hard_timeout=0,priority=%s,arp,nw_dst=%s,actions=output:%s"'%  (switch,PrefixPriority,prefixIP,preficPort)
					os.system(cmd)
					cmd='ovs-ofctl add-flow %s -O OpenFlow13 "table=0, idle_timeout=0,hard_timeout=0,priority=%s,ip,nw_dst=%s,actions=output:%s"'%  (switch,PrefixPriority,prefixIP,preficPort)
					os.system(cmd)
				#up
				cmd='ovs-ofctl add-group %s -O OpenFlow13 "group_id=5,type=select,bucket=output:%s,bucket=output:%s"'%(switch,3,4)
				os.system(cmd)
				cmd='ovs-ofctl add-flow %s -O OpenFlow13 "table=0,priority=100,arp,actions=group:5"'%(switch)
				os.system(cmd)
				cmd='ovs-ofctl add-flow %s -O OpenFlow13 "table=0,priority=100,ip,actions=group:5"'%(switch)
				os.system(cmd)	
				
		#core switch only down flows			
		for j in range(1,k/2+1):
			for i in range(1,k/2+1):
				switch=str(4)+"_"+str(j)+"_"+str(i)
				#cmd = "sudo ovs-vsctl set bridge %s protocols=OpenFlow13" % switch
				#os.system(cmd)
				for p in range(0,k):
					prefixIP=str(10)+"."+str(p)+"."+str(0)+"."+str(0)+"/"+str(16)
					preficPort=p+1
					PrefixPriority=32768
					#cmds.append(str("prefix =="+switch+","+prefixIP+","+str(preficPort)))
					cmd='ovs-ofctl add-flow %s -O OpenFlow13 "table=0, idle_timeout=0,hard_timeout=0,priority=%s,arp,nw_dst=%s,actions=output:%s"'%  (switch,PrefixPriority,prefixIP,preficPort)
					os.system(cmd)
					cmd='ovs-ofctl add-flow %s -O OpenFlow13 "table=0, idle_timeout=0,hard_timeout=0,priority=%s,ip,nw_dst=%s,actions=output:%s"'%  (switch,PrefixPriority,prefixIP,preficPort)
					os.system(cmd)
		#return cmds			
					 
					

