import numpy

class Net(object):
	"""A sparse matrix"""

	def __init__(self):
		self._nodes={}
		self.type="py"

	def _legaledge(self, src, dst):
		# Override this for symmetrical/two-way linked ones
		return True

	def _intsetedge(self, src, dst, val):
		# Override this for symmetrical/two-way linked ones
		if val==0:
			if src in self._nodes:
				del self._nodes[src][dst]
				if len(self._nodes[src])==0:
					#delete isolated node
					del self._nodes[src]
		else:
			if not src in self._nodes:
				self._nodes[src]={dst: val}
			else:
				self._nodes[src][dst]=val
	
	def _setedge(self, src, dst, val):
		assert self._legaledge(src, dst)
		self._intsetedge(src, dst, val)
		assert self._legaledge(src, dst)

	def __getitem__(self, args):
		if isinstance(args, tuple):
			if len(args) != 2:
				raise KeyError, "Don't be silly. One or two indices"
			assert self._legaledge(args[0],args[1])
			try:
				retval=self._nodes[args[0]][args[1]]
			except KeyError:
				return 0
			return retval
		else:
			return Node(self, args)
		
	def __setitem__(self, key, val):
		if isinstance(key, tuple):
			if len(key) != 2:
				raise KeyError, "Don't be silly. One or two args"
			self._setedge(key[0], key[1], val) 
			return val
		else:
			if isinstance(val, Node):
				if val.index in val.net._nodes:
					val=val.net._nodes[val.index]
				else:
					val={}
			if not isinstance(val, dict):
				raise NotImplemented, \
						"Setting nodes only implemented from maps"
			del self[key] # calls __delitem__
			# We perform a deep copy
			for edge in val.iteritems():
				self._setedge(key, edge[0], edge[1])
			return Node(self, key)
	
	def __delitem__(self, args):
		if isinstance(args, tuple):
			if len(args) != 2:
				raise KeyError, "Don't be silly. One or two indices"
			self._setedge(args[0], args[1], 0)
		else:
			for dest in self[args]:
				# self[args] returns a node, for which .iter()
				self[args,dest]=0

	def __iter__(self):
		return self._nodes.keys().__iter__()

	def isSymmetric(self):
		return False

	def __len__(self):
		return len(self._nodes)

class Node(object):
	def __init__(self, net, index):
		self.net=net;
		self.index=index;

	def __iter__(self):
		if not self.index in self.net._nodes:
			return iter([])
		return self.net._nodes[self.index].keys().__iter__()
		#return self.net._nodes[self.index].__iter__()

	def __getitem__(self, index):
		return self.net[self.index, index]

	def __setitem__(self, index, val):
		 self.net[self.index, index]=val
		 return val

	def deg(self):
		return len(self.net._nodes[self.index])

class SymmNet(Net):
	"""A net with forced symmetry"""
	def _legaledge(self, src, dst):
		if src in self._nodes:
			if dst in self._nodes[src]:
				return dst in self._nodes \
						and src in self._nodes[dst] \
						and self._nodes[src][dst]==self._nodes[dst][src]
		#either no src or no edge src->dst
		return dst not in self._nodes or src not in self._nodes[dst]

	def _intsetedge(self, src, dst, val):
		Net._intsetedge(self, src, dst, val)
		Net._intsetedge(self, dst, src, val)
		return val
				
	def isSymmetric(self):
		return True
			
class FullNet(Net):
	def __init__(self,size):
		super(Net,self)
		self.size=size
		#self._nodes=FullNet.Nodes(size)
		self._nodes=numpy.zeros([size,size])
		
	def _intsetedge(self, src, dst, val):				
		self._nodes[src][dst]=val		

	def __getitem__(self,args):
		if isinstance(args,tuple):
			return self._nodes[args[0],args[1]]
		else:
			return FullNode(self,args)						
			
	def __iter__(self):
		return range(0,self.size).__iter__()

	def __len__(self):
		return self.size

	def getWeightMatrix(self):
		return self._nodes
		
class FullNode(Node):
	def __iter__(self):
		for i in range(0,self.net.size):
			if self.net[self.index,i]!=0:
				yield i

	def deg(self):
		#this is slow, maybe you should have these in memory
		return len(list(self))

class SymmFullNet(FullNet):
	def _intsetedge(self, src, dst, val):				
		self._nodes[src][dst]=val		
		self._nodes[dst][src]=val		

	def isSymmetric(self):
		return True



try:
	from cnet import pynet_c
	#from cnet.pynet_c import SymmNet as SymmNet_c	
	class SymmNet(pynet_c.SymmNet_c,Net):
		pass
	class Node_(pynet_c.Node_c,Node):
		pass
	pynet_c.Node_c=Node_

except ImportError:
	print "Loading C interface failed."


if __name__ == '__main__':
    """Run unit tests if called."""
    from tests.test_pynet import *
    unittest.main()
