This Python module includes 4 files. Here is a short description about the contents of those files:

---pynet.py:
This module holds in the basic classes needed for network datastructures. Do not make any changes here to
add functionality. 

---netext.py:
Collection of functions that are not suitable for any other module. This file also contains extensions for
the basic classes defined in pynet.py.

---netio.py:
Basic input/output functions for the networks, ie. writing and reading network files in different formats.

---percolator.py:
A module for percolation analysis of networks. This currently include link percolation, node percolation and 3-clique 
percolation.

For list of methods and classes in modules use help([modulename])

----- Example of use ------
>>>from netpython import * 	# imports all modules
>>>net=pynet.SymmNet()		# creates a symmetric network 
>>>net[1][2]=1			# adds a link between nodes 1 and 2
>>>net[2][3]=100			
>>>net[1,3]=1000		# == net[1][3]=1000
>>>for neighbor in net[1]:	# loop through adjacent nodes of node 1
>>> print neighbor		
2				
3
>>>len(net.edges)		# number of edges in the net
3

>>>pgpNet=loadNet("nets/pgp_2003_final.edg") # reads network from a file
>>>drawNet(pgpNet) # draws the net using Himmeli and displays it on the screen
...
