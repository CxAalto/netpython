import pynet,netext,percolator
import random


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
    numberOfNodes=len(net)
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

            netext.copyNodeProperties(net,mst)

            return mst

    # else it is a forest

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

    netext.copyNodeProperties(net,newNet)

    return newNet


def collapseIndices(net,returnIndexMap=False):
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

    netext.copyNodeProperties(net,newNet)

    if returnIndexMap:
        return newNet,indexmap
    else:
        return newNet


def threshold_by_value(net,threshold,mode,keepIsolatedNodes=False):
    '''Generates a new network by thresholding the input network. 
       If using option keepIsolatedNodes=True, all nodes in the
       original network will be included in the thresholded network;
       otherwise only those nodes which have links will remain (this
       is the default). 
    
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

    # Add isolated nodes to the network. Because there is no function
    # for adding a node, such as SymmNet.addNode(), this must be done
    # using a hack: trying to read a link
    if keepIsolatedNodes==True:
        for node in net:
            newnet[node][node]
            
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
    return getSubnet(net,keep_these_nodes)

def getSubnet(net,nodes):
    """Get induced subgraph.

    Parameters
    ----------
    net: pynet.Net, pynet.SymmNet or pynet.SymmFullNet
        The original network.
    nodes : sequence
        The nodes that span the induces subgraph.

    Return
    ------
    subnet : type(net)
        The induced subgraph that contains only nodes given in
        `nodes` and the edges between those nodes that are
        present in `net`. Node properties etc are left untouched.
    """
    
    # Different schemes are required for FullNets and Nets.
    # For Nets, vertex names are kept.
    # For FullNets, rows are removed from the matrix so vertex
    # labels change. This has to be taken into account when
    # copying node properties from the original to the filtered matrix.

    if (isinstance(net,pynet.SymmFullNet)):
        newnet = pynet.SymmFullNet(len(nodes))

        # First make a dict such keys=keep_these_nodes,
        # values=0...keep_these_nodes this dict maps the original row
        # indices to a smaller number of row indices
        nodedict={}
        for i,node in enumerate(nodes):
            nodedict[node]=i

        # Then go through the list of edges and build new matrix by
        # looping through edges and add each
        for n_i, n_j, w_ij in net.edges:
            if (n_i in nodes) and (n_j in nodes):
                newnet[nodedict[n_i]][nodedict[n_j]] = w_ij

        #  ----- handling node properties --------------

        if hasattr(net,'nodeProperty'):
            # First copy the list of properties, if any.
            for node_property in net.nodeProperty:
                netext.addNodeProperty(newnet, node_property)

            # Then copy properties of all nodes in `keep_these_nodes`.
            for node in nodes:
                for np in newnet.nodeProperty:
                    newnet.nodeProperty[np][nodedict[node]] = net.nodeProperty[np][node]

    elif isinstance(net, (pynet.Net, pynet.SymmNet)):
        # Handle both directed and undirected networks.
        newnet = type(net)() # Initialize to same type as `net`.
        degsum=0
        for node in nodes:
            degsum += net[node].deg()
        if degsum >= len(nodes)*(len(nodes)-1)/2:
            othernodes=set(nodes)
            for node in nodes:
                if net.isSymmetric():
                    othernodes.remove(node)
                for othernode in othernodes:
                    if net[node,othernode]!=0:
                        newnet[node,othernode]=net[node,othernode]
        else:
            for node in nodes:
                for neigh in net[node]:
                    if neigh in nodes:
                        newnet[node,neigh]=net[node,neigh]
                
        netext.copyNodeProperties(net, newnet)

    return newnet


    


def collapseBipartiteNet(net,nodesToRemove):
    """
    Returns an unipartite projection of a bipartite network.
    """
    newNet=pynet.SymmNet()
    for node in nodesToRemove:
        degree=float(net[node].deg())
        for node1 in net[node]:
            for node2 in net[node]:
                if node1.__hash__()>node2.__hash__():
                    newNet[node1,node2]=newNet[node1,node2]+1.0/degree

    netext.copyNodeProperties(net,newNet)
    return newNet

def local_threshold_by_value(net,threshold):
    '''Generates a new network by thresholding the input network.
       Inputs: net = network, threshold = threshold value,
       mode = 0 (accept weights < threshold), 1 (accept weights > threshold)
       Returns a network. Note! threshold is really alpha which is defined in
       "Extracting the multiscale backbone of complex weighted networks"
       http://www.pnas.org/content/106/16/6483.full.pdf'''

    newnet=pynet.SymmNet()
    for node in net:
        s=net[node].strength()
        k=net[node].deg()
        for neigh in net[node]:
            w=net[node,neigh]
            if (1-w/s)**(k-1)<threshold:
                newnet[node,neigh]=w
    netext.copyNodeProperties(net,newnet)

    return newnet

		
def netConfiguration(net,keepsOrigNet=False,seed=0):
	"""
	netConfiguration:
		This function generates the configuration network of an incoming arbitrary net. 
		It keeps the degree of each node but randomize the edges between them.
		
		Incoming parameters:
			net
			keepsOrigNet(=False) - optional
			seed - optional
		Outgoing parameters:
			configuration_net - the shuffled network
	"""
	if seed!=0:
		random.seed(int(seed))

	newNet=pynet.SymmNet()
	if keepsOrigNet:
		testNet=pynet.SymmNet()
		for edge in net.edges:
			testNet[edge[0],edge[1]]=edge[2]	
	else:
		testNet=net
	edgeList=[]
		
	for edge in net.edges:
		edgeList.append(edge)
		
	firstEdgeID=0
	while firstEdgeID !=(len(edgeList)):
		
		secondEdgeID=firstEdgeID
		
		while secondEdgeID==firstEdgeID:
			secondEdgeID=random.randint(0,len(edgeList)-1)
		
		if (edgeList[firstEdgeID][1]==edgeList[secondEdgeID][0]) or (edgeList[secondEdgeID][1]==edgeList[firstEdgeID][0]):
			continue
		if (edgeList[firstEdgeID][1]==edgeList[secondEdgeID][0]) and (edgeList[secondEdgeID][1]==edgeList[firstEdgeID][0]):
			continue
		if (edgeList[firstEdgeID][0]==edgeList[secondEdgeID][0]) or (edgeList[firstEdgeID][1]==edgeList[secondEdgeID][1]):
			continue
		if (newNet[edgeList[firstEdgeID][0],edgeList[secondEdgeID][1]]>0.0) or (newNet[edgeList[secondEdgeID][0],edgeList[firstEdgeID][1]]>0.0):
			continue
		if (testNet[edgeList[firstEdgeID][0],edgeList[secondEdgeID][1]]>0.0) or (testNet[edgeList[secondEdgeID][0],edgeList[firstEdgeID][1]]>0.0):
			continue
		
		edgeList[firstEdgeID][1]+=edgeList[secondEdgeID][1]
		edgeList[secondEdgeID][1]=edgeList[firstEdgeID][1]-edgeList[secondEdgeID][1]
		edgeList[firstEdgeID][1]=edgeList[firstEdgeID][1]-edgeList[secondEdgeID][1]
		
		newNet[edgeList[firstEdgeID][0],edgeList[secondEdgeID][1]]=0.0
		newNet[edgeList[secondEdgeID][0],edgeList[firstEdgeID][1]]=0.0

		testNet[edgeList[firstEdgeID][0],edgeList[secondEdgeID][1]]=0.0
		testNet[edgeList[secondEdgeID][0],edgeList[firstEdgeID][1]]=0.0
	
		newNet[edgeList[firstEdgeID][0],edgeList[firstEdgeID][1]]=1.0
		newNet[edgeList[secondEdgeID][0],edgeList[secondEdgeID][1]]=1.0
		testNet[edgeList[firstEdgeID][0],edgeList[firstEdgeID][1]]=1.0
		testNet[edgeList[secondEdgeID][0],edgeList[secondEdgeID][1]]=1.0
		
		firstEdgeID+=1
		
	return newNet

    
if __name__ == '__main__':
    """Run unit tests if called."""
    from tests.test_transforms import *
    unittest.main()
