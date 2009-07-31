"""
This module contains percolator functions and some related data structures.
This contains general framework for edge and node percolation studies, but
also functions for k-clique percolation.
"""

import pynet,netext,array,math,netio,communities, numpy,transforms
from operator import mul



class KtreeInteger_new:
    def __init__(self,size=0):
        self.ktree=numpy.ones(size)
        self.subTreeWeight=numpy.ones(size)
        self.mappingOn=False
        self.sizeDistribution={}
        self.sizeDistribution[1]=size
        if size!=0:
            for index in xrange(0,size):
                self.ktree[index]=index;
        
    def __getRealParent(self,node):
        """
        Private method. Reads elements directly from the tree.        
        """
        try:
            return self.ktree[node]
        except IndexError:
            self.setSize(node)
            return node

    def __setRealParent(self,node,newParent):
        """
        Private.
        """
        try:
            self.ktree[node]=newParent
        except IndexError:
            self.setSize(node)
            self.ktree[node]=newParent        

    def getSetIndex(self,node):
        parent=self.__getRealParent(node)
        if node!=parent:
            self.__setRealParent(node,self.getSetIndex(parent))
        return self.__getRealParent(node)

            
    def mergeSets(self,node1,node2):
        set_of_node1=self.getSetIndex(node1)
        set_of_node2=self.getSetIndex(node2)
        if set_of_node1!=set_of_node2:
            if self.subTreeWeight[set_of_node1]>self.subTreeWeight[set_of_node2]:
                large_set,small_set=set_of_node1,set_of_node2
            else:
                large_set,small_set=set_of_node2,set_of_node1 

            small_set_size=self.subTreeWeight[small_set]
            large_set_size=self.subTreeWeight[large_set]
            self.sizeDistribution[small_set_size]-=1
            self.sizeDistribution[large_set_size]-=1
            #we remove empty elements
            if self.sizeDistribution[small_set_size]==0:
                self.sizeDistribution.__delitem__(small_set_size)
            if self.sizeDistribution[large_set_size]==0:
                self.sizeDistribution.__delitem__(large_set_size)
            
            self.sizeDistribution[small_set_size+large_set_size]=self.sizeDistribution.get(small_set_size+large_set_size,0)+1
            self.subTreeWeight[large_set]+=self.subTreeWeight[small_set]

            self.__setRealParent(small_set,large_set)

    def mergeSetsWithElements(self,elements):
        first=elements[0]
        for i in range(1,len(elements)):
            self.setParent(elements[i],first)

    def __iter__(self):
        for i in self.ktree:
            yield i

    def getCommStruct(self,separateElements=True):
        communityMap={}
        if self.mappingOn:
            nodes=self.ktree
        else:
            nodes=range(0,len(self.ktree))
        
        for node in nodes:
            communityKey=self.getParent(node)
            if separateElements or communityKey!=node:
                if communityKey not in communityMap:
                    communityMap[communityKey]=[node]
                else:
                    communityMap[communityKey].append(node)

        return communities.NodeFamily(communityMap)

    def __len__(self):
        return len(self.ktree)


    def addEdge(self,edge):
        self.setParent(edge[0],edge[1])
       
    def setSize(self,newSize):
        for index in range( len(self.ktree),newSize+1):
           self.ktree.append(index);

class KtreeInteger:
    def __init__(self,size=0):
        self.ktree=[]
        self.mappingOn=False
        if size!=0:
            for index in range(0,size+1):
                self.ktree.append(index);

        
    def __getRealParent(self,node):
        """
        Private method. Reads elements directly from the tree.        
        """
        try:
            return self.ktree[node]
        except IndexError:
            self.setSize(node)
            return node

    def __setRealParent(self,node,newParent):
        """
        Private.
        """
        try:
            self.ktree[node]=newParent
        except IndexError:
            self.setSize(node)
            self.ktree[node]=newParent

    def getParent(self,node):
        parent=self.__getRealParent(node)
        if node!=parent:
            self.__setRealParent(node,self.getParent(parent))
        return self.__getRealParent(node)
            
    def setParent(self,node,newParent):
        self.__setRealParent(self.getParent(node),self.getParent(newParent))

    def __iter__(self):
        for i in self.ktree:
            yield i

    def getCommStruct(self,separateElements=True):
        communityMap={}
        if self.mappingOn:
            nodes=self.ktree
        else:
            nodes=range(0,len(self.ktree))
        
        for node in nodes:
            communityKey=self.getParent(node)
            if separateElements or communityKey!=node:
                if communityKey not in communityMap:
                    communityMap[communityKey]=[node]
                else:
                    communityMap[communityKey].append(node)

        return communities.NodeFamily(communityMap)

    def __len__(self):
        return len(self.ktree)

    def mergeSetsWithElements(self,elements):
        first=elements[0]
        for i in range(1,len(elements)):
            self.setParent(elements[i],first)

    def addEdge(self,edge):
        self.setParent(edge[0],edge[1])
       
    def setSize(self,newSize):
        for index in range( len(self.ktree),newSize+1):
           self.ktree.append(index);



#class KtreeMapping(KtreeInteger):
class Ktree(KtreeInteger):
    """
    A Kruskal tree with mapping frontend. This means that node names can be any
    hashable objects.
    """
    def __init__(self,size=0):
        self.ktree=KtreeInteger(size)
        self.nodeIndex=netext.Enumerator()
        self.mappingOn=True

    def getParent(self,node):
        return self.nodeIndex.getReverse(self.ktree.getParent(self.nodeIndex[node]))
    def setParent(self,node,newParent):
        self.ktree.setParent(self.nodeIndex[node],self.nodeIndex[newParent])

    def __iter__(self):
        return self.nodeIndex.__iter__()

    def getCommStruct(self):
        cs=self.ktree.getCommStruct()
        newcs=communities.NodeFamily()
        for c in cs:
            newc=[]
            for node in c:
                newc.append(self.nodeIndex.getReverse(node))
            newcs._addCommunity(newc)
            #newcs.comm.append(newc)
        return newcs

class Percolator:
    def __init__(self,edgesAndEvaluations,buildNet=True):
        self.edges=edgesAndEvaluations
        self.buildNet=buildNet

    def __iter__(self):
        if self.buildNet:
            net=pynet.SymmNet()
        ktree=Ktree()
        for edge in self.edges:
            if isinstance(edge,EvaluationEvent):
                cs=ktree.getCommStruct()
                cs.threshold=edge.threshold
                cs.addedEdges=edge.addedElements
                if self.buildNet:
                    cs.net=net
                yield cs
            else:
                ktree.addEdge(edge)
                if self.buildNet:
                    net[edge[0],edge[1]]=edge[2]


class EvaluationList:
    """
    EvaluationList object is an iterable object that iterates through a list returning
    EvaluationEvent objects according to given rules.
    Todo: better behavior when stacking evaluationlists
    """
    def __init__(self,thelist,weightFunction=lambda x:x[2]):
        self.thelist=thelist
        self.weightFunction=weightFunction
        self.strengthEvaluations=False
        self.evaluationPoints=[]
        self.lastEvaluation=False
    def setEvaluations(self,evaluationPoints):
        self.evaluationPoints=evaluationPoints
    def setLinearEvaluations(self,first,last,numberOfEvaluationPoints):
        self.strenghtEvaluations=False
        if last<=first:
            raise Exception("last<=first")
        if numberOfEvaluationPoints<2:
            raise Exception("Need 2 or more evaluation points")
        last=last-1
        self.setEvaluations(map(lambda x:int(first+(last-first)*x/float(numberOfEvaluationPoints-1)),range(0,numberOfEvaluationPoints)))
        self.lastEvaluation=False
    def setStrengthEvaluations(self):
        self.strengthEvaluations=True
        self.lastEvaluation=False
    def setLastEvaluation(self):
        self.lastEvaluation=True
    def __iter__(self):
        if not self.strengthEvaluations and not self.lastEvaluation:
            index=0
            evalIter=self.evaluationPoints.__iter__()
            nextEvaluationPoint=evalIter.next()
            for element in self.thelist:
                yield element
                if index==nextEvaluationPoint:
                    yield EvaluationEvent(self.weightFunction(element),index+1)
                    nextEvaluationPoint=evalIter.next()
                index+=1
        elif not self.lastEvaluation:
            last=None
            numberOfElements=0
            for element in self.thelist:
                numberOfElements+=1
                #print str(element)+"          \r", #debug purposes only
                if last!=self.weightFunction(element) and last!=None:
                    yield EvaluationEvent(last,numberOfElements-1)
                last=self.weightFunction(element)
                yield element
            yield EvaluationEvent(last,numberOfElements)

        else:
            for element in self.thelist:
                yield element
            yield EvaluationEvent()
        
def getComponents(net):
    edges=net.edges
    ee=EvaluationList(edges)
    ee.setLastEvaluation()
    p=Percolator(ee)
    for cs in p:
        return cs

def getKCliqueComponents(net,k):
    """
    Returns community structure calculated with k-clique percolation.
    >>> n=netio.loadNet('nets/co-authorship_graph_cond-mat_small.edg')
    >>> getKCliqueComponents(n,5).getSizeDist()=={5: 36, 6: 9, 7: 4, 8: 2}
    True
    """
    def evaluateAtEnd(edges):
        for edge in edges:
            yield edge
        yield EvaluationEvent()
    edgesAndEvaluations=evaluateAtEnd(net.edges)

    kcliques=kcliquesByEdges(edgesAndEvaluations,k) #unweighted clique percolation        
    for community in communitiesByKCliques(kcliques):
        return community


class KClique(object):
    """
    A class for presenting cliques of size k. Realizations
    of this class just hold a sorted list of nodes in the clique.
    """
    def __init__(self,nodelist,notSorted=True):
        self.nodes=nodelist
        if notSorted:
            self.nodes.sort()
        self.hash=None
    def __hash__(self):
        #this function is very important for speed
        if self.hash==None:
            #self.hash=hash(reduce(mul,self.nodes))
            self.hash=hash(reduce(mul,map(self.nodes[0].__class__.__hash__,self.nodes)))
            #self.hash=str.__hash__(reduce(lambda x,y:x+y,map(str,self.nodes)))
            #self.hash=int.__hash__(sum(map(self.nodes[0].__class__.__hash__,self.nodes)))
        return self.hash
    def __iter__(self):
        for node in self.nodes:
            yield node
    def __cmp__(self,kclique):
        if self.nodes==kclique.nodes:
            return 0
        else:
            return 1
    def __add__(self,kclique):
        return KClique(self.nodes+kclique.nodes)
    def getSubcliques(self):
        for i in range(0,len(self.nodes)):
            yield KClique(self.nodes[:i]+self.nodes[(i+1):],notSorted=False)
    def __str__(self):
        return str(self.nodes)
    def getEdges(self):
	for node in self.nodes:
	    for othernode in self.nodes:
		if node!=othernode:
		   yield (node,othernode)
    def getK(self):
	return len(self.nodes)

def getIntensity(kclique,net):
    intensity=0
    for edge in kclique.getEdges():
	intensity*=net[edge[0],edge[1]]
    return pow(intensity,1.0/float(kclique.getK()))

class EvaluationEvent:
    def __init__(self,threshold=None,addedElements=None):
        self.threshold=threshold
        self.addedElements=addedElements

def kcliquesAtSubnet(nodes,net,k):
    """
    List all k-cliques at a given network. Any implementation is fine,
    but as this routine is a part of a clique percolator anyway we
    will use itself to find cliques larger than 2. Cliques of size 1 and
    2 are trivial.
    """
    if len(nodes)>=k:
        if k==1:
            for node in nodes:
                yield KClique([node])
        elif k==2:
            subnet=netext.getSubnet(net,nodes)
            for edge in subnet.edges:
                yield KClique([edge[0],edge[1]])
        else:
	    subnet=netext.getSubnet(net,nodes)
	    for kclique in kcliquesByEdges(subnet.edges,k):
		yield kclique

def kcliquesByEdges(edges,k):
    """
    Generator function that generates a list of cliques of size k in the order they
    are formed when edges are added in the order defined by the 'edges' argument.
    If many cliques is formed by adding one edge, the order of the cliques is
    arbitrary.
    This generator will pass through any EvaluationEvent objects that are passed to
    it in the 'edges' generator.
    """
    newNet=pynet.SymmNet() # Edges are added to a empty network one by one
    for edge in edges:
        if isinstance(edge,EvaluationEvent):
            yield edge
        else:
            # First we find all new triangles that are born when the new edge is added
            triangleEnds=set() # We keep track of the tip nodes of the new triangles
            for adjacentNode in newNet[edge[0]]: # Neighbor of one node of the edge ...
                if newNet[adjacentNode,edge[1]]!=0: #...is a neighbor of the other node of the edge...
                    triangleEnds.add(adjacentNode) #...then the neighbor is a tip of a new triangle

            # New k-cliques are now (k-2)-cliques at the triangle end points plus
            # the two nodes at the tips of the edge we are adding to the network
            for kclique in kcliquesAtSubnet(triangleEnds,newNet,k-2):
                yield kclique+KClique([edge[0],edge[1]])

            newNet[edge[0],edge[1]]=edge[2] # Finally we add the new edge to the network

def kcliquesWeight(net,k,weightFunction):
    kcliques=list(kcliquesByEdges(net.edges,k))
    kcliques.sort(lambda x,y: cmp(weightFunction(x,net),weightFunction(y,net)))
    for kclique in kcliques:
        yield kclique

def communitiesByKCliques(kcliques):
    # Calculate the neighboring relations
    krTree=Ktree()
    for kcliqueNumber,kclique in enumerate(kcliques):
        if isinstance(kclique,EvaluationEvent):
            communityStructure=krTree.getCommStruct().getCollapsed()
            communityStructure.threshold=kclique.threshold
            communityStructure.numberOfEdges=kclique.addedElements
            communityStructure.numberOfKCliques=kcliqueNumber+1
            yield communityStructure
        else:
            #for fewer operations at ktree, names of new cliques should be saved
            #and given to ktree when merging the sets
            krcliques=list(kclique.getSubcliques()) #list all k-1 cliques that are subcliques
            krTree.mergeSetsWithElements(krcliques) #merge the sets of k-1 cliques at the list 


def kcliquePercolator(net,k,start,stop,evaluations,reverse=False,weightFunction=None):    
    if weightFunction==None:
        edges=list(net.edges)
        edges.sort(lambda x, y: cmp(x[2],y[2]),reverse=reverse)
        edgesAndEvaluations=EvaluationList(edges)
        edgesAndEvaluations.setLinearEvaluations(start,stop,evaluations)
        kcliques=kcliquesByEdges(edgesAndEvaluations,k) #unweighted clique percolation
    else:    
        kcliques=EvaluationList(kcliquesWeight(net,k,weightFunction),weightFunction=lambda x:getIntensity(x,net))
        kcliques.setLinearEvaluations(start,stop,evaluations) 

    for community in communitiesByKCliques(kcliques):
        yield community
        

def getKCliqueBipartiteNet(net,k):
    """
    Returns a bipartite network where to partitions are k-cliques and 
    (k-1)-cliques in the net that is given as a parameter. There is a link
    between a k-clique and (k-1)-clique if the (k-1)-clique is a subclique of 
    the k-clique.
    """

    kcliques=set()
    krcliques=set()
    kbinet=pynet.SymmNet()
    for kclique in kcliquesByEdges(net.edges,k):
        kcliques.add(kclique)
        for krclique in kclique.getSubcliques():
            krcliques.add(krclique)
            kbinet[kclique,krclique]=1
    return kbinet,kcliques,krcliques

def getKCliqueNet(net,k):
    """
    Returns a network of k-cliques in the network given as a parameter.
    Two k-cliques are adjacent if they share a (k-1)-clique.
    """
    kbinet,kcliques,krcliques=getKCliqueBipartiteNet(net,k)
    return transforms.collapseBipartiteNet(kbinet,krcliques)

def getKRCliqueNet(net,k):
    """
    Returns a network of (k-1)-cliques, which are subcliques of some k-clique in the
    network given as a parameter.
    Two (k-1)-cliques are adjacent if they are subcliques of the same k-clique.
    """
    krnet=pynet.SymmNet()
    for kclique in kcliquesByEdges(net.edges,k):
        krcliques=list(kclique.getSubcliques())
        for krclique in krcliques:
            for krclique2 in krcliques:
                krnet[krclique][krclique2]=1
    return krnet
                
