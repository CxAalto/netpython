"""Extra functions and other extensions for pynet datastructures

    Extensions
    ----------
        Net.edges        
        Node.edges
        Net.add(net)

    Functions
    ---------
        getSubnet(net,nodes) (to be moved to extensions?)
        collapseIndices(net)
        deg(net)
        degMap(net)
        clustering(net)
        snowball(net,startingnodeindex,depth)
        drawNet(net)
        mst(net)
        mst_kruskal(net)
        makeER(n,p)
        fullNet(nodes,weight=1)
        collapseBiNet(net,nodes)

    Other
    -----
        Enumerator        
        NodeFamily
        communityTree
        Himmeli
"""
import pynet,os,netio
import random
import heapq
import string
import percolator
import shutil
import copy
from PIL import Image

class Net_edges:
    def __init__(self,net):
        self.net=net
    def __iter__(self):
         for node1Index in self.net:
            node1=self.net[node1Index]
            for node2Index in node1:
                #if self.net.__class__!=pynet.SymmNet or node1Index<node2Index:
		if (not self.net.isSymmetric()) or node1Index.__hash__()<node2Index.__hash__():
                    yield [node1Index,node2Index,self.net[node1Index,node2Index]]       
    def __len__(self):
        lenght=0
        for nodeIndex in self.net:
            lenght+=len(self.net[nodeIndex].edges)
        if self.net.isSymmetric():
            return lenght/2
        else:
            return lenght
    def __str__(self):
        return str(list(self))
        #rs=""
        #for edge in self:
        #    rs+=str(edge)+" "
        #return rs
pynet.Net.edges=property(Net_edges)

class Net_weights:
    def __init__(self,net):
        self.net=net
    def __iter__(self):
        for edge in self.net.edges:
            yield edge[2]
    def __len__(self):
        return len(self.net.edges)
    def __str__(self):
        return reduce(lambda x,y: str(x)+" "+str(y),self)
pynet.Net.weights=property(Net_weights)

class Node_edges:
    def __init__(self,node):
        self.node=node
    def __iter__(self):
        for index in self.node:
            yield self.node.net[self.node.index,index]       
    def __len__(self):
        return self.node.deg()
        #return len(self.node.net._nodes[self.node.index])
    def __str__(self):
        rs=""
        for edge in self:
            rs+=str(edge)+"\t"
        return rs
pynet.Node.edges=property(Node_edges)


def getStrength(node):
    return sum(node.edges)
pynet.Node.strength=getStrength

def strengths(net,nodes=None):
    strengths={}
    if nodes==None:
        nodes=net
    for node in nodes:
        strengths[node]=net[node].strength()
    return strengths


def Net_add(self,net):
    for node in net:
        for neigh in net[node]:
            self[node,neigh]=net[node,neigh]
pynet.Net.add=Net_add


class NodeProperties(dict):
    def __init__(self):
        super(dict,self)
        self.__dict__={}
    def addProperty(self,propertyName):
        if not hasattr(self,propertyName):
            newValue={}
            self[propertyName]=newValue
            self.__setattr__(propertyName,newValue)
            
def addNodeProperty(net,propertyName):
    if not hasattr(net,"nodeProperty"):
        net.nodeProperty=NodeProperties()
    net.nodeProperty.addProperty(propertyName)
    #if not hasattr(net.nodeProperty,propertyName):
    #    newValue={}
    #    #net.nodeProperty.__setattr__(propertyName,newValue)
    #    net.nodeProperty[propertyName]=newValue

def copyNodeProperties(fromNet,toNet):
    if hasattr(fromNet,"nodeProperty"):
        for p in fromNet.nodeProperty:
            addNodeProperty(toNet,p)
            for node in toNet:
                value=fromNet.nodeProperty[p][node]
                toNet.nodeProperty[p][node]=value


def getSubnet(net,nodes):
    if net.isSymmetric():        
        newNet=pynet.SymmNet()
    else:
        newNet=pynet.Net()
    degsum=0
    for node in nodes:
        degsum+=net[node].deg()
    if degsum>=len(nodes)*(len(nodes)-1)/2:
        othernodes=set(nodes)
        for node in nodes:
            if net.isSymmetric():
                othernodes.remove(node)
            for othernode in othernodes:
                if net[node,othernode]!=0:
                    newNet[node,othernode]=net[node,othernode]
    else:
        for node in nodes:
            for neigh in net[node]:
                if neigh in nodes:
                    newNet[node,neigh]=net[node,neigh]
    return newNet


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




def deg(net):
    degrees={}
    for node in net:
        degrees[node]=net[node].deg()
    return degrees


def fullNet(nodes,weight=1):    
    net=pynet.SymmNet()
    for node1 in nodes:
        for node2 in nodes:
            net[node1,node2]=weight
    return net

            
#def collapseBiNet(net,nodes):
#    newNet=pynet.SymmNet()
#    for node in nodes:
#        newNet.add(fullNet(list(net[node])))


def collapseBiNet(net,nodesToRemove):
    newNet=pynet.SymmNet()
    for node in nodesToRemove:
        degree=float(net[node].deg())
        for node1 in net[node]:
            for node2 in net[node]:
                if node1.__hash__()>node2.__hash__():
                    newNet[node1,node2]=newNet[node1,node2]+1.0/degree
    return newNet

def getMeanDistance(theSet,distanceFunction):
    l=list(theSet)
    n=0
    s=0.0
    for i in l:
        for j in l:
            if i.__hash__()>j.__hash__():
                s+=distanceFunction(i,j)
                n+=1
    return s/float(n)


def getPathLengths(net,startingNode):
    edge=set([startingNode])
    interior=set()
    pathlengths={}
    i=0
    while len(edge)>0:
     i+=1
     interior=edge.union(interior)
     newEdge=set()
     for node in edge:
      for neighbor in net[node]:
	if neighbor not in interior:
	 newEdge.add(neighbor)
         pathlengths[neighbor]=i
     edge=newEdge
    return pathlengths
