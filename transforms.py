import pynet,netext,percolator
import random

# Changes
#
# 01.06.09 JS : Added copyNodeProperties to every function - node properties are inherited to transformed nets!
# 01.06.09 JS : Added filterNet - input: network + list of nodes to keep, output: network with these nodes
# 01.06.09 LK : Modified the documentation of threshold_by_value to match the implementation.

def mst(net,maximum=False):
    """Find a minimum/maximum spanning tree

    """
    return mst_kruskal(net,True,maximum)

def mst_kruskal(net,randomize=True,maximum=False):
    """Find a minimum/maximum spanning tree using Kruskal's algorithm

    If random is set to true and the mst is not unique, a random
    mst is chosen.

    >>> t=pynet.SymmNet()
    >>> t[1,2]=1
    >>> t[2,3]=2
    >>> t[3,1]=3
    >>> m=mst_kruskal(t)
    >>> print m.edges
    [[1, 2, 1], [2, 3, 2]]
    """
    edges=list(net.edges)
    if randomize:
        random.shuffle(edges) #the sort has been stable since python version 2.3
    edges.sort(lambda x,y:cmp(x[2],y[2]),reverse=maximum)
    mst=pynet.SymmNet()
    numberOfNodes=len(net._nodes)
    #ktree=percolator.Ktree(numberOfNodes)
    ktree=percolator.Ktree() #just use dict
    addedEdges=0
    for edge in edges:
        if ktree.getParent(edge[0])!=ktree.getParent(edge[1]):
            mst[edge[0],edge[1]]=edge[2]
            ktree.setParent(edge[0],edge[1])
            addedEdges+=1

        if addedEdges==numberOfNodes-1:
            #the mst is a tree
            return mst

    #the mst is a forest

    netext.copyNodeProperties(net,mst)

    return mst


def snowball(net,startingnodeindex,depth):
    startingnode=net[startingnodeindex]
    newNet=pynet.Net()
    toVisit=set()
    toVisit.add(startingnode.index)
    newToVisit=set()
    visited=set()
    for d in range(1,depth+1):
        print "Depth: ",d," visited ", len(visited)," to visit ", len(toVisit)
        visited=visited|toVisit
        for nodeIndex in toVisit:
            #visited.add(nodeIndex)
            node=net[nodeIndex]
            for newIndex in node:
                newNode=net[newIndex]
                newNet[node.index][newIndex]=net[node.index][newIndex]
                newNet[newIndex][node.index]=net[node.index][newIndex]
                if newIndex not in visited:
                    newToVisit.add(newIndex)

        toVisit=newToVisit
        newToVisit=set()

    netext.copyNodeProperties(net,newnet)

    return newNet


def collapseIndices(net):
    """
    Chances the indices of net to run from 0 to len(net)-1
    """

    newNet = pynet.Net()
    indexmap = {}
    index = 0

    for i in net:
        if net[i].deg() != 0:
            indexmap[i] = index;
            index += 1
    
    for i in net:
        for j in net[i]:
            if net[j][i] != 0:
                newNet[indexmap[i]][indexmap[j]] = net[i][j]
                newNet[indexmap[j]][indexmap[i]] = net[j][i]

    netext.copyNodeProperties(net,newnet)


    return newNet


def threshold_by_value(net,threshold,mode):
    '''Generates a new network by thresholding the input network.
       Inputs: net = network, threshold = threshold value,
       mode = 0 (accept weights < threshold), 1 (accept weights > threshold)
       Returns a network.'''

    newnet=pynet.SymmNet()
    edges=list(net.edges)
    if mode == 0:
        for edge in edges:
            if (edge[2] < threshold):
                newnet[edge[0],edge[1]]=edge[2]
    elif mode == 1:
        for edge in edges:
            if (edge[2] > threshold):
                newnet[edge[0],edge[1]]=edge[2] 
    else:
        raise Exception("mode must be either 0 or 1.")

    netext.copyNodeProperties(net,newnet)
                
    return newnet


def dist_to_weights(net,epsilon=0.001):
    '''Transforms a distance matrix / network to a weight
    matrix / network using the formula W = 1 - D / max(D).
    Returns a matrix/network'''

    N=len(net._nodes)

    if (isinstance(net,pynet.SymmFullNet)):
        newmat=pynet.SymmFullNet(N)
    else:
        newmat=pynet.SymmNet()    

    edges=list(net.edges)

    maxd=0.0
    for edge in edges:
        if edge[2]>maxd:
            maxd=edge[2]

    # epsilon trick; lowest weight will be almost but
    # not entirely zero
    
    maxd=maxd+epsilon

    for edge in edges:
        if not(edge[2]==maxd):
            newmat[edge[0]][edge[1]]=1-edge[2]/maxd

    netext.copyNodeProperties(net,newmat)

        
    return newmat

def filterNet(net,keep_these_nodes):
    '''Takes a network net, and returns a network newnet with only those nodes listed in keep_these_nodes.
       Node properties etc are left untouched.'''

    
    N=len(net._nodes)

    if (isinstance(net,pynet.SymmFullNet)):
        newnet=pynet.SymmFullNet(N)
    else:
        newnet=pynet.SymmNet()
    
    edges=list(net.edges)

    for edge in edges:

        if (edge[0] in keep_these_nodes) and (edge[1] in keep_these_nodes):

            newnet[edge[0]][edge[1]]=edge[2]

    netext.copyNodeProperties(net,newnet)

    return newnet

    




    
