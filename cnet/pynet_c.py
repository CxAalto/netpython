"""
Python bindings to a C++ impelementation of a graph.
Todo:
numeric iterator for net
"""

import numpy
import _cnet





class SymmNet_c(object):
	"""A sparse matrix"""

	def __init__(self,numeric=False):
		#self._nodes={}
		self.type="cnet"
		self._net=_cnet.new_Sn(0)
		self.numeric=numeric
		if numeric:
			self._setEdge=self._setEdge_numeric
			self._getEdge=self._getEdge_numeric			
		else:
			self._nodes=Enumerator()
			

	def _setEdge(self,node1,node2,value):
		_cnet.Sn_setEdge(self._net,self._nodes[node1],self._nodes[node2], value)	

	def _setEdge_numeric(self,node1,node2,value):
		_cnet.Sn_setEdge(self._net,node1,node2, value)	

	def _getEdge(self,node1,node2):
		return _cnet.Sn_getEdge(self._net,self._nodes[node1],self._nodes[node2])
	def _getEdge_numeric(self,node1,node2):
		return _cnet.Sn_getEdge(self._net,node1,node2)

	def __getitem__(self, args):
		if isinstance(args, tuple):
			if len(args) != 2:
				raise KeyError, "Don't be silly. One or two indices"
			return self._getEdge(args[0],args[1])
			#return _cnet.Sn_getEdge(self._net,self._nodes[args[0]],self._nodes[args[1]])
		else:
			return Node_c(self, args)
		
	def __setitem__(self, key, val):
		if isinstance(key, tuple):
			if len(key) != 2:
				raise KeyError, "Don't be silly. One or two args"
			self._setEdge(key[0],key[1],val)
			#_cnet.Sn_setEdge(self._net,self._nodes[key[0]],self._nodes[key[1]], val) 
			return val
		else:
			raise NotImplemented
	
	def __delitem__(self, args):
		if isinstance(args, tuple):
			if len(args) != 2:
				raise KeyError, "Don't be silly. One or two indices"
			self._setEdge(args[0],args[1],0)
			#_cnet.Sn_setEdge(self._net,self._nodes[args[0]],self._nodes[args[1]], 0) 
		else:
			for dest in self[args]:
				# self[args] returns a node, for which .iter()
				self._setEdge(dest,args,0)
				#_cnet.Sn_setEdge(self._net,self._nodes[dest],self._nodes[args], 0) 

	def __iter__(self):
		if self.isNumeric():
			return xrange(len(self)).__iter__()
		else:
			return self._nodes.__iter__()

	def isSymmetric(self):
		return True

	def isNumeric(self):
		return self.numeric

	def __len__(self):
		if self.isNumeric:
			return _cnet.Sn_getSize(self._net)
		else:
			return len(self._nodes)

	def __del__(self):
		_cnet.delete_Sn(self._net)

class Node_c(object):
	def __init__(self, net, index):
		self.net=net;
		self.index=index;

	def __iter__(self):
		return NodeIterator(self.net,self.index)

	def __getitem__(self, index):
		return self.net[self.index, index]

	def __setitem__(self, index, val):
		 self.net[self.index, index]=val
		 return val

	def deg(self):
		if self.net.isNumeric():
			return _cnet.Sn_getDegree(self.net._net,self.index)
		else:
			return _cnet.Sn_getDegree(self.net._net,self.net._nodes[self.index])

class NodeIterator:
	def __init__(self,net,node):
		self.net=net
		cnet=net._net
		if self.net.isNumeric():
			self.citerator=_cnet.Sn_getNeighborIterator(cnet,node)
		else:
			self.citerator=_cnet.Sn_getNeighborIterator(cnet,net._nodes[node])
	def next(self):
		next=_cnet.NeighborIterator_getNext(self.citerator)
		if next==-1:
			_cnet.delete_NeighborIterator(self.citerator)
			raise StopIteration
		if not self.net.isNumeric():
			next=self.net._nodes.getReverse(next)
		return next

class Enumerator:
    """
    Finds enumeration for hashable items. For new items a new number is
    made up and if the item already has a number it is returned instead
    of a new one.
    >>> e=Enumerator()
    >>> e['foo']
    0
    >>> e['bar']
    1
    >>> e['foo']
    0
    >>> list(e)
    ['foo', 'bar']
    """
    def __init__(self):
        self.number={}
        self.item=[]

    def _addItem(self,item):
        newNumber=len(self.number)
        self.number[item]=newNumber
        self.item.append(item)
        return newNumber

    def __getitem__(self,item):
        try:
            return self.number[item]
        except KeyError:
            return self._addItem(item)
 
    def getReverse(self,number):
        return self.item[number]

    def __iter__(self):
        return self.number.__iter__()

    def __len__(self):
        return len(self.number)

	




