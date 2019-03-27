#!/usr/bin/python
from ecmp import *

if __name__=='__main__':
	ec=ecmpPaths()
	path=ec.getPath("10.0.0.2","10.0.0.3")
	print(len(path))
	for p in path:
		print(p)
