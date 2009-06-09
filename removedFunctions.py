"""
This module contains old implementations or othrewise obsolete classes and functions
For developement purposes only.
"""

class Percolator_old:
    def __init__(self,edges,evaluations,size=0):
        """
        Edges to put in the network and points on the edges vector where to evaluate.
        Edges and evaluations must be iterable.
        """
        #If size is not given or is zero, the size for the network is searched from the
        #given edge list.
        #"""
        self.edges=edges
        self.evaluations=evaluations
        self.size=size 

    def __iter__(self):
        """
        Returns the next community structure in evaluation points after adding corresponding number of edges
        to the net.
        Evaluations are done when number of edges added indicated by element in evaluation vector is reached.
        If -1 is a element in evaluation vector, then rest of the edges are added to the net and resulting
        component structure is returned.        
        """

        #Implementation of this method is a mess, the author of this code pleads you not to read any further
        tree=Ktree(self.size)

        currentEdgeIndex=0
        edgeIterator=self.edges.__iter__()
        notEnd=True
        lastEvaluationPoint=None

        for evaluationPoint in self.evaluations:
            while notEnd and evaluationPoint!=currentEdgeIndex:                 
                try:
                    edge=edgeIterator.next()
                    tree.addEdge(edge)
                    currentEdgeIndex+=1
                except StopIteration:
                    notEnd=False

            yield tree.getCommStruct()

            lastEvaluationPoint=evaluationPoint

        if lastEvaluationPoint==-1:
            yield tree.getCommStruct()

        raise StopIteration



class NodePercolator(Percolator_old):
    def __init__(self,net,nodes,evaluationPoints,nodeEvaluations=True):
        """
        Initializes node percolator
        net = the network where percolation is to take place
        nodes = list of node indices giving the order where nodes are to be added to the net 
        evaluationPoints = list of indices of nodes where evaluation of percolation is to happen
        nodeEvaluations = True if evaluationpoints are for nodes and False if they are for links
        """
        self.net=net
        self.nodes=nodes
        self.evaluationPoints=evaluationPoints

        #inverse map of node orders for faster edge order evaluations
        self.nodeOrder={}
        for i in range(0,len(nodes)):
            nodeIndex=nodes[i]
            self.nodeOrder[nodeIndex]=i

        edges=[]
        if nodeEvaluations:
            edgeEvaluationPoints=[]
        else:
            edgeEvaluationPoints=evaluationPoints
        index=-1

        #convert the ordered list of nodes to ordered list of edges
        #and find evaluation places in the resulting edge vector
        for node1Index in nodes:
            node1=net[node1Index]
            for node2Index in node1:
                node2=net[node2Index]
                if self.nodeOrder[node1Index]>self.nodeOrder[node2.index]:
                    edges.append([node1Index,node2.index])
                    index+=1
            if nodeEvaluations:
                if node1Index in evaluationPoints:
                    edgeEvaluationPoints.append(index+1)

        #debug
        #print len(edgeEvaluationPoints)
        #yhden liian lyhyt?!
        edgeEvaluationPoints.append(-1)


        Percolator.__init__(self,edges,edgeEvaluationPoints)
    


class PercolatorGenerator:
    """
    This class helps user to create percolators by implementing rules for order of
    nodes and links to be added and evaluations to be made.
    Rules for evaluation points can be given for both nodes and links if order is
    defined for nodes, but only for links if order is defined for links.
    """
    def __init__(self,net):
        self.net=net
        self.hasEvaluations=False
        self.hasOrder=False
        self.nodeEvaluations=False

    def nodeEvaluationPercents(self,evaluationPoints):
        """
        Defines evaluation points for nodes from a list of percents of
        nodes at network in each evaluation point.
        """
        maxPoint=len(self.net)
        self.evaluationPoints=map(lambda x:math.floor(x*maxPoint),evaluationPoints)
        self.hasEvaluations=True
        self.nodeEvaluations=True


    def nodeLinearEvaluations(self,numberOfEvaluations):
        self.nodeEvaluationPercents(map(lambda x:x/float(numberOfEvaluations),range(0,numberOfEvaluations)))
        self.nodeEvaluations=True

    def nodeEvaluationIndex(self,evaluationPoints):
        self.evaluationPoints=evaluationPoints
        self.hasEvaluations=True
        self.nodeEvaluations=True

    def linkEvaluationPercents(self,evaluationPoints):
        numberOfLinks=sum(netext.deg(self.net))/2
        maxPoint=numberOfLinks
        evaluationPoints=map(lambda x:math.floor(x*maxPoint),evaluationPoints)
        self.linkEvaluationIndex(evaluationPoints)

    def linkLinearEvaluations(self,numberOfEvaluations):
        self.linkEvaluationPercents(map(lambda x:x/float(numberOfEvaluations),range(0,numberOfEvaluations)))
    
    def linkEvaluationIndex(self,evaluationPoints):
        self.nodeEvaluations=False
        self.hasEvaluations=True
        #evaluationPoints.append(-1)
        self.evaluationPoints=evaluationPoints
    
    def nodeOrder(self,nodeOrder):
        self.nodeOrder=nodeOrder
        self.hasOrder=True

    def nodeOrderProperty(self,nodePropertyMap,ascending=True):
        if ascending:
            c=1
        else:
            c=-1
            
        self.nodeOrder=sorted(nodePropertyMap,lambda x,y:c*cmp(nodePropertyMap[x],nodePropertyMap[y]))
        self.hasOrder=True

    def nodeOrderBy(self,nodeProperty,ascending=True):
        raise NotImplementedError

    def getPercolator(self):
        if not self.hasEvaluations:
            raise UnboundLocalError,'no evaluation points defined for percolator'
        if not self.hasOrder:
            raise UnboundLocalError,'no order defined for percolator'

        return NodePercolator(self.net,self.nodeOrder,self.evaluationPoints,nodeEvaluations=self.nodeEvaluations)





def getComponents_old(net):
    """
    Returns CommStruct object of nodes in different components
    """
    edges=net.edges
    #edges=net.edges
    p=Percolator(edges,[-1])
    for cs in p:
        return cs


def cp3(net):
    """
    A 3-clique percolator implementation	
    """
    treelen=len(netext.getEdges(net))
    net2=pynet.Net()
    t3=Ktree(treelen)
    c2=[None] #None is because otherwise indexin would start from 0 and it is not a valid weight
    for edge in net.edges():
        if net2[edge[0]].deg()!=0  and net2[edge[1]].deg()!=0:
             for elem in net2[edge[0]]:
                node3Index=elem.key
                #print edge[0],",",edge[1],",",node3Index
                if net2[node3Index][edge[1]]!=0:
                    #print "node added"
                    t3.addEdge([len(c2),net2[edge[0]][node3Index]])
                    t3.addEdge([len(c2),net2[edge[1]][node3Index]])
        net2[edge[0]][edge[1]]=len(c2)
        net2[edge[1]][edge[0]]=len(c2) #symmetry
        #print edge[0]," ",edge[1]," ",len(c2)
        c2.append([edge[0],edge[1]])

    return t3.getCommStruct(False).getNewCommStruct(c2)
