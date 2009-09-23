import pynet,netext
import numpy as np
import info_theory as ith
import operator
#from logger import log

def printname(fun):
    """Decorator for identifying the called method.
    """
    def new_fun(obj, *args):
        print "<%s.%s>" % (obj.__class__.__name__, fun.__name__)
        return fun(obj, *args)
    return new_fun

class NodeCover(object):
    """Representation of possibly overlapping node partitions."""
    
    def __init__(self, cmap=None, inputFile=None, N_nodes=None):
        if cmap is None:
            cmap = {}

        self._comm = []
        for community in cmap:
            self._addCommunity(cmap[community])
        if inputFile is not None:
            self._parseStrings(inputFile)
        self._sortBySize()

        # Find out the number of nodes if not given.
        if N_nodes is None:
            all_nodes = set()
            for c in self._comm:
                all_nodes.update(c)
            N_nodes = len(all_nodes)
            del all_nodes
        self.N_nodes = N_nodes

    def _addCommunity(self,newCommunity):
        self._comm.append(set(newCommunity))

    def _parseStrings(self,input):
        for line in input:
            fields = map(int, line.split())
            self._addCommunity(fields)

    def _sortBySize(self):
        self._comm.sort(key=len, reverse=True)     

    @property
    def comm(self):
        return self._comm

    def __str__(self):
        string=""
        for community in self.comm:
            for node in community:
                string=string+str(node)+" "
            string=string[0:len(string)-1]+"\n"
        return string
   
    def __getitem__(self,index):
        return self.comm[index]

    def __len__(self):
        return len(self.comm)

    def __iter__(self):
        for c in self.comm:
            yield c

    def getCommunitySizes(self):
        """Return list of community sizes."""
        return map(len, self.comm)

    def getGiant(self):
        """Get the largest component as a set of nodes.
        """
        return self.comm[0]

    def getGiantSize(self):
        """Get the size of the largest component.
        """
        return self.getCommunitySizes()[0]

    def getSizeDist(self):
        """Get size distribution.
        
        Return
        ------
        sizeDist : dict {community_size: count}
           The community size distribution where the community sizes
           are keys and the number of communities of that size is the
           value.
        """
        dist = {}
        for cs in self.getCommunitySizes():
            dist[cs] = 1 + dist.get(cs, 0)
        return dist

    def getSusceptibility(self, size=None):
        """Return the susceptibility.

        Susceptibility is defined as: 
        
        (Sum_{s!=size(gc)} n_s * s * s) / (Sum_{s!=size(gc)} n_s * s)

        Size is the number of nodes in the network. If it is given, it
        is assumed that communities of size 1 are not included in this
        community structure.  If there is only 0 or 1 community, zero
        is returned.
        """
        sd = self.getSizeDist()
        
        if len(sd) < 1:
            if size==None or size==0:
                return 0.0
            else:
                return 1.0

        sizeSum = 0
        for key, value in sd.iteritems():
            sizeSum += key*value

        # If no size is given, assume that also communities of size 1
        # are included.
        if size==None:
            sus=0
            size=sizeSum
        else:
            sus=size-sizeSum #s=1
            assert(sus>=0)

        # Remove largest component
        gc = max(sd.keys())
        sd[gc] = 0

        # Calculate the susceptibility
        for key, value in sd.iteritems():
            sus += value*key**2
        if (size-gc) == 0:
            return 0.0
        else:
            return float(sus)/float(size-gc)

    def getCollapsed(self):
        """

        """
        newcs = NodeCover()
        for community in self._comm:
            newCommunity = set()
            for oldnode in community:
                for newnode in oldnode:
                    newCommunity.add(newnode)

            newCommunityArray=[]
            for node in newCommunity:
                newCommunityArray.append(node)
            newcs._addCommunity(newCommunityArray)

        newcs._sortBySize()
        return newcs

    def getNew(self,newNodes):
        """
        Returns new community structure based on this one and
        new nodes denoted by indices on this one
        """
        newcs=NodeCover({})
        for community in self._comm:
            newCommunity=set()
            for oldnode in community:
                for newnode in newNodes[oldnode]:
                    newCommunity.add(newnode)

            newCommunityArray=[]
            for node in newCommunity:
                newCommunityArray.append(node)
            newcs._addCommunity(newCommunityArray)

        newcs._sortBySize()
        return newcs

    def _getOverlapNetwork(self, other):
        """Create a bipartite network from overlapping nodes.

        Nodes correspond to communities and edge weight is the number
        of common nodes between the two communities. Nodes [0
        ... len(self)-1] correspond to communities in self, and nodes
        [len(self) ... len(self)+len(other)] correspond to
        communities in `other`.
        """

        def create_commIDs(comm):
            """Construct commIDs.

            The key is node ID, and the value will be a list of
            community IDs this node belongs to.
            """
            commIDs = {}
            for c_num, c in enumerate(comm):
                for node in c:
                    commIDs.setdefault(node, []).append(c_num)
            return commIDs

        # Find out the number of nodes.
        N = max(self.N_nodes, other.N_nodes)

        # Construct community ID dictionaries.
        cID_A = create_commIDs(self.comm)
        cID_B = create_commIDs(other.comm)

        # Construct the bipartite community net.
        Nc_A = len(self.comm)
        commNet = pynet.SymmNet()
        for node in xrange(N):
            try:
                for cj in cID_B[node]:
                    cj += Nc_A
                    for ci in cID_A[node]:
                        commNet[ci, cj] += 1
            except AttributeError:
                # `node` does not occur in one of the node
                # covers. Skip this node.
                continue

        return commNet

    def getMaxVariationOfInformation(self, otherCover):
        """Return maximum variation of information.

        The maximum variation of information can be used to compare
        two families with overlapping node set.

        The definition comes from Appendix B of
          Andrea Lancichinetti, Santo Fortunato, Janos Kertesz (2009)
          `Detecting the overlapping and hierarchical community
          structure of complex networks'.

        Parameters
        ----------
        otherCover : NodeCover object
           The other community sructure to compare with.
        N_nodes : int
           The total number of nodes in all communities. If None, the
           size of the union of all communities in both community
           structures is used. Note that if there are nodes that do
           not belong in any community this will not give the correct
           answer.

        Return
        ------
        mv : float
           The maximum variation of information.

        Notes
        -----
        Time complexity is roughly O(N)+O(M^2), where N is the total
        number of nodes and M is largest number of communities for one
        node.

        If one community structure consists of only one community
        covering all nodes, this measure is always 0.5 (unless of
        course the other one is identical, in which case 1.0 is
        returned.)
        """
        def p_log2_p(p):
            return (0.0 if p == 0 else -p*np.log2(p))
        
        # Find out the number of nodes.
        Nf = float(max(self.N_nodes, otherCover.N_nodes))

        # Construct bipartite community network.
        commNet = self._getOverlapNetwork(otherCover)
        Nc_A = len(self)
        Nc_B = len(otherCover)

        # List of community sizes.
        comm_sizes = self.getCommunitySizes() + otherCover.getCommunitySizes()

        # DEBUG ::: 1697546 2532174 844023 1688153
        print len(commNet), len(comm_sizes), len(self), len(otherCover)

        ret_val = 1.0
        for IX, IY in [(xrange(Nc_A), xrange(Nc_A, Nc_A+Nc_B)),
                       (xrange(Nc_A, Nc_A+Nc_B), xrange(Nc_A))]:
            # IX contains the IDs of first communities (first node
            # cover), IY the IDs of the second communities. These are
            # flipped on the second iteration to calculate the same
            # thing the other way around.
            H_norm = []
            for X_k in IX:
                # Calculate the entropies H(X_k|Y_l) for all Y_l in IY
                # and find the minimum. H_min is initialized to
                # H(X_k), which is the maximum value and will be the
                # final value if no Y_l is accepted.
                px = comm_sizes[X_k]/Nf
                H_min = H_X = ith.entropy_X([px, 1-px])
                for Y_l in commNet[X_k]:
                    cut_size = commNet[X_k][Y_l]
                    union_size = comm_sizes[X_k] + comm_sizes[Y_l] - cut_size
                    hP_same = (p_log2_p(cut_size/Nf)
                               + p_log2_p((Nf - union_size)/Nf))
                    hP_diff = (p_log2_p((comm_sizes[X_k] - cut_size)/Nf)
                               + p_log2_p((comm_sizes[Y_l] - cut_size)/Nf))
                    if (hP_same > hP_diff):
                        py = comm_sizes[Y_l]/Nf
                        H_Y = ith.entropy_X([py, 1-py])
                        H_min = min(H_min, hP_same + hP_diff - H_Y)

                        #print (X_k, Y_l, hP_same, hP_diff, hP_same > hP_diff,
                        #       (hP_same + hP_diff - H_Y)/H_X)
                H_norm.append((0 if H_X == 0 else H_min/H_X))

            ret_val -= 0.5*sum(H_norm)/len(IX)
            #print H_norm, sum(H_norm)/len(IX)

        return ret_val


    def getMaxVariationOfInformation_slow(self, otherCover, N_nodes=None):
        """Return maximum variation of information.

        Note that the time complexity is O(N*M), where N is the number
        of communities in `self` and M is the number of communities in
        `otherCover`.
        """

        def p_log2_p(p):
            return (0.0 if p == 0 else -p*np.log2(p))

        # Find out the number of nodes if not given. `Nf` is defined
        # just to make the code more readable.
        if N_nodes is None:
            all_nodes = set()
            for c in self.comm:
                all_nodes.update(c)
            N_nodes = len(all_nodes)
            del all_nodes
        Nf = float(N_nodes)

        ret_val = 1.0
        for XF, YF in [(self.comm, otherCover.comm),
                       (otherCover.comm, self.comm)]:
            H_norm = []
            for X_k in XF:
                # Calculate the entropies H(X_k|Y_l) for all Y_l in YF
                # and find the minimum. H_min is initialized to
                # H(X_k), which is the maximum value and will be the
                # final value if no Y_l is accepted.
                px = len(X_k)/Nf
                H_min = H_X = ith.entropy_X([px, 1-px])
                for Y_l in YF:
                    cut_size = len(X_k.intersection(Y_l))
                    hP_same = (p_log2_p(cut_size/Nf)
                               + p_log2_p((Nf - len(X_k.union(Y_l)))/Nf))
                    hP_diff = (p_log2_p((len(X_k) - cut_size)/Nf)
                               + p_log2_p((len(Y_l) - cut_size)/Nf))
                    if (hP_same > hP_diff):
                        py = len(Y_l)/Nf
                        H_Y = ith.entropy_X([py, 1-py])
                        H_min = min(H_min, hP_same + hP_diff - H_Y)

                        #print (X_k, Y_l, hP_same, hP_diff, hP_same > hP_diff,
                        #       (hP_same + hP_diff - H_Y)/H_X)
                H_norm.append((0 if H_X == 0 else H_min/H_X))

            ret_val -= 0.5*sum(H_norm)/len(XF)
            #print H_norm, sum(H_norm)/len(XF)

        return ret_val


class NodePartition(NodeCover):
    """Representation of node partitions.

    Each node must belong to exactly one partition.  Node names must
    be integers from 0 to N-1, where N is the number of nodes in the
    network.
    """

    def __init__(self, cmap=None, inputFile=None, N_nodes=None):
        """Initialize a node partition.

        A node partition can be made based on a dictionary or read
        from a file, or both. Communities will be sorted according to
        size in decreasing order, so that community ID of 0 refers to
        the largest community.

        Parameters
        ----------
        cmap : dict {community_ID: [node_1, node_2, ...], ...}
            A dictionary where keys correspond to community IDs and
            the value is a list of nodes in that community.
        inputFile : file object
            File to read the node partition from. Each line must have
            one community, with the nodes separated by whitespace.
        N_nodes : int
            The total number of nodes in the network. If None, it will
            be assumed to be the total number of nodes read from
            `cmap` and `inputFile`.
        """
        if cmap is None:
            cmap = {}

        # Read data from inputfile and add the read communities to
        # cmap. The key in cmap does not matter, so we use integers
        # starting from len(cmap) as long as they are not already in
        # cmap.
        print len(cmap), inputFile.name
        if inputFile is not None:
            c_index = len(cmap)
            for line in inputFile:
                while c_index in cmap:
                    c_index += 1
                cmap[c_index] = map(int, line.split())
                c_index += 1

        # Create a list [(len(comm), comm_ID), ...] and sort it in
        # decreasing order.
        comm_sizes = [(len(comms), commID) for commID, comms in cmap.iteritems()]
        comm_sizes.sort()
        comm_sizes.reverse()

        # Construct a dictionary {node_ID: comm_ID} so that comm_ID is
        # ordered by community size (largest = 0)
        self._commIDs = {} # Dictionary of community IDs of each node.
        for newCommID, (s, oldCommID) in enumerate(comm_sizes):
            for node in cmap[oldCommID]:
                self._commIDs[node] = newCommID
        self.N_communities = len(cmap) + 1

        # List of community sizes.
        self.C_sizes = map(operator.itemgetter(0), comm_sizes)

        # If `N_nodes` is not given, use the number of nodes just read.
        if N_nodes is None:
            N_nodes = len(self._commIDs)
        self.N_nodes = N_nodes

        # Save calculated mutual informations with other
        # nodePartitions into `self.MIs`. This way mutual information
        # is not calculated again if for example
        # getNormalizedMutualInformation is called after calling
        # getMutualInformation.
        self.MIs = {}

    def __len__(self):
        return self.N_communities

    @property
    def comm(self):
        """List of community sets.

        Uses the same community indices as self._commIDs. Because the
        original community indices have been chosen based on the
        community size, there is no need to sort self._comm again.
        """
        try:
            return self._comm
        except AttributeError:
            self._comm = [set() for i in range(self.N_communities)]
            for node, commID in self._commIDs.iteritems():
                self._comm[commID].add(node)
            return self._comm

    def _getOverlapNetwork(self, other):
        """Create a bipartite network from overlapping nodes.

        Nodes correspond to communities and edge weight is the number
        of common nodes between two communities. Nodes [0
        ... len(self)-1] correspond to communities in self, and nodes
        [len(self) ... len(self)+len(otherCover)] correspond to
        communities in `other`.
        """
        commNet = pynet.SymmNet()
        for node in self._commIDs:
            ci = self._commIDs[node]
            cj = self.N_communities + other._commIDs[node]
            commNet[ci, cj] += 1
        return commNet

    def getSetsForNodes(self):
        """Return a map of nodes to the set it belongs."""
        return self.commIDs

    def getCommunitySizes(self):
        """Return list of community sizes."""
        return self.C_sizes

    @property
    def entropy(self):
        """Entropy of the node partition."""
        try:
            return self._entropy
        except AttributeError:
            len_c = self.C_sizes
            self._entropy = ith.entropy_X(np.array(len_c)/float(sum(len_c)))
            return self._entropy

    def getMutualInformation_slow(self, otherPartition):
        """Calculate mutual information.

        Note that the time complexity of this algorithm is O(N*M),
        where N is the number of communities in self and M is the
        number of communities in `otherPartition`.
        """
        mi=0.0
        n=float(sum(map(len,list(self))))
        for c in self:
            n_i=float(len(c))
            for c2 in otherPartition:
                n_j=float(len(c2))
                n_ij=float(len(c.intersection(c2)))
                if n_ij!=0:
                    mi += n_ij/n*np.log2(n_ij*n/n_i/n_j)
        return mi

    def getMutualInformation(self, otherPartition):
        """Calculate mutual information.

        Time complexity is O(N+E), where N is the number of nodes
        and E is the number of overlapping pairs of communities.
        """
        # Check if mutual information has already been calculated.
        if id(otherPartition) in self.MIs:
            return self.MIs[id(otherPartition)]
        
        commNet = self._getOverlapNetwork(otherPartition)

        # Calculate mutual information.
        mi=0.0
        n = self.N_nodes
        for ci, cj, n_ij in commNet.edges:
            ci, cj = min(ci, cj), max(ci, cj)-self.N_communities
            n_i = self.C_sizes[ci]
            n_j = otherPartition.C_sizes[cj]
            mi += n_ij/n*np.log2(n_ij*n/n_i/n_j)

        # Add this mutual information to the list of already
        # calculated mutual informations.
        self.MIs[id(otherPartition)] = mi
        otherPartition.MIs[id(self)] = mi

        return mi

    def getNormalizedMutualInformation(self,otherPartition):
        """Return normalized mutual information.

        The normalized mutual information is
             I_n(X;Y) = 2*I(X;Y)/(H(X)+H(Y))
        I_n(X;Y) is always in [0, 1].
        """
        return (2*self.getMutualInformation(otherPartition)
                /(self.entropy + otherPartition.entropy))

    def getMImetric(self,otherPartition):
        """Return a metric based on mutual information.

        The returned value is
             D(X,Y) = 1 - I(X;Y)/max{H(X), H(Y)}
        D(X,Y) is a metric: it is symmetric, non-negative, satisfies
        the triangle inequality and D(X,Y)=0 if and only if X==Y.
        """
        return 1.0 - (self.getMutualInformation(otherPartition)
                      /max(self.entropy, otherPartition.entropy))
        



class communityTree:
    """
    >>> test=[[set([1,2,3,4,5])],[set([1,2,3]),set([4,5])],[set([1]),set([2]),set([3]),set([4]),set([5])]]
    >>> test.reverse()
    >>> t=communityTree(test)
    >>> print t.tree
    [[None], [0, 0], [0, 0, 0, 1, 1]]
    """
    def __init__(self,cslist):
        cslist.reverse()
        self.tree=[]
        self.cslist=cslist
        self.tree.append([])

        self.net=pynet.SymmNet()
        #self.multiplier=10**ceil(np.log10(len(cslist)))
        
        #add roots:
        for c in cslist[0]:
            self.tree[0].append(None)

        #go through each level and add links:
        for thisLevel in range(1,len(cslist)):
            self.tree.append([])
            for communityIndex in range(0,len(cslist[thisLevel])):
               self.tree[thisLevel].append(None)
               for fatherIndex in range(0,len(cslist[thisLevel-1])):
                    if cslist[thisLevel][communityIndex]<=cslist[thisLevel-1][fatherIndex]:
                        self.tree[thisLevel][communityIndex]=fatherIndex
                        #self.net[str((thisLevel,communityIndex)),str((thisLevel-1,fatherIndex))]=1
                        self.net[self._getNameByNode((thisLevel,communityIndex)),self._getNameByNode((thisLevel-1,fatherIndex))]=len(cslist)+1-thisLevel
                        #self.net[self._getNameByNode((thisLevel-1,fatherIndex)),self._getNameByNode((thisLevel,communityIndex))]=1
                        break
        cslist.reverse()

    def _getNodeByName(self,name):
        f=name.split(',')
        return (int(f[0]),int(f[1]))
        pass
    def _getNameByNode(self,node):
        return reduce(lambda x,y:str(x)+","+str(y),node)
        #return str(node)
        #return node[0]+node[1]*self.multiplier        

    def _getLeafOrderInTree(self):
        order=[(0,0)]
        for level in range(1,len(self.tree)):
            replace={}
            for i in range(0,len(self.tree[level])):
                father=(level-1,self.tree[level][i])
                if father in replace:
                    replace[father]+=[(level,i)]
                else:
                    replace[father]=[(level,i)]
            for father in replace.keys():
                fi=order.index(father)
                order=order[0:fi]+replace[father]+order[fi+1:]
        return order

    def getNodeCoordinatesByWeight(self,weightFunction,xscale=1,yscale=1):
        self.cslist.reverse()
        coords={}
        for nodeName in self.net:
            node=self._getNodeByName(nodeName)
            y=node[0]
            x=weightFunction(self.cslist[node[0]][node[1]])
            coords[nodeName]=(float(xscale)*float(x),float(yscale)*float(y))
        self.cslist.reverse()
        return coords

    def getNodeCoordinates(self,xscale=1,yscale=1,sizeRelativeX=True):
        coords={}
        nodex={}
        for i,leaf in enumerate(self._getLeafOrderInTree()):
            nodex[leaf]=float(i)
            #coords[self._getNameByNode(leaf)]=(float(i),float(leaf[0]))

        for level in range(len(self.tree)-1,-1,-1):
            merged=[]
            lastfather=None
            links=list(enumerate(self.tree[level]))
            links.sort(lambda x,y: cmp(x[1],y[1]))
            links.append((None,None))
            #print links
            for i,father in links:
                #print "father: "+str(father)
                if father==lastfather and i<len(links):
                    if father!=None:
                        merged+=[i]
                else:
                    if len(merged)>0:
                        s=float(0)
                        norming=float(0)
                        #print merged
                        for mergee in merged:
                            if sizeRelativeX:
                                size=len(self.cslist[len(self.cslist)-1-level][mergee])
                            else:
                                size=1
                            norming+=size
                            s+=float(nodex[(level,mergee)])*size
                        nodex[(level-1,lastfather)]=s/norming#/float(len(merged))
                        #print "Added position for node: " + str((level-1,lastfather))
                    merged=[i]


                lastfather=father

        for node in nodex.keys():
            coords[self._getNameByNode(node)]=(float(xscale)*float(nodex[node]),float(yscale)*float(node[0]))

        return coords
            
    def getTree(self):
        return self.tree

    def getTreeAsNet(self,thinning=True):
        if thinning:
            newNet=pynet.SymmNet()
            for edge in self.net.edges:
                newNet[edge[0],edge[1]]=1#edge[2]
            for node in self.net:
                if newNet[node].deg()==2:
                    l=list(newNet[node])
                    n1=self._getNodeByName(l[0])
                    n2=self._getNodeByName(l[1])
                    me=self._getNodeByName(node)
                    if n1[0]<me[0]:
                        parent=n1
                        child=n2
                    else:
                        parent=n2
                        child=n1
                    if newNet[self._getNameByNode(parent)].deg()==2:
                        newNet[node,l[0]]=0
                        newNet[node,l[1]]=0
                        newNet[self._getNameByNode(parent),self._getNameByNode(child)]=1
            return newNet
        else:
            return self.net


def expandLeavesOnLeveltree(tree):
    def isLeaf(tree,com,level):
        if level==len(tree)-1:
            return False        
        for c2 in tree[level+1]:
            if c2.issubset(com):
                return False
        return True
    leaves=[]
    for l,cs in enumerate(tree):
        for c in cs:
            if isLeaf(tree,c,l):
                leaves.append((c,l))
    for leaf in leaves:
        for level in range(leaf[1]+1,len(tree)):
            tree[level].comm.append(leaf[0])
            tree[level]._sortBySize()
            


if __name__ == '__main__':
    """Run unit tests if called."""
    from tests.test_communities import *
    unittest.main()
