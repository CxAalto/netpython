import pynet,netext
from math import log
import numpy as np
import info_theory as ith

#class CommStruct:
class NodeFamily(object):
    """
    Defines a community structure of a network.
    WARNING: Name of this class was changed

    To be implemented:
    *reading from string

    """
    
    #def __init__(self):
    #    self.comm=[]

    def __init__(self, cmap={}, inputFile=None):
        self.comm=[]
        for community in cmap:
            self._addCommunity(cmap[community])
        if inputFile is not None:
            self._parseStrings(inputFile)
        self._sortBySize()

    def _parseStrings(self,input):
        for line in input:
            fields = map(int, line.split())
            self._addCommunity(fields)

    def __str__(self):
        string=""
        for community in self.comm:
            for node in community:
                string=string+str(node)+" "
            string=string[0:len(string)-1]+"\n"
        return string

    def _sortBySize(self):
        self.comm.sort(key=len, reverse=True)     
        
    def _addCommunity(self,newCommunity):
        self.comm.append(set(newCommunity))

    def __getitem__(self,index):
        return self.comm[index]

    def __len__(self):
        return len(self.comm)

    def __iter__(self):
        for c in self.comm:
            yield c

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
        for c in self.comm:
            dist[len(c)] = 1 + dist.get(len(c), 0)
        return dist

    def getGiant(self):
        """Get the largest component as a set of nodes.
        """
        maxsize=0
        largest=None
        for community in self.comm:
            if len(community)>maxsize:
                maxsize=len(community)
                largest=community

        return largest

    def getGiantSize(self):
        """Get the size of the largest component.
        """
        giant = self.getGiant()
        return (0 if giant is None else len(giant))

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

        # If no size is given, assume that also communities of size 1 are included
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
        newcs = NodeFamily()
        for community in self.comm:
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
        newcs=NodeFamily({})
        for community in self.comm:
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


    def getSetsForNodes(self):
        """
        Returns a map of nodes to the set it belongs.
        Sets are denoted by integers so that largest
        community has smallest number etc.
        """
        nodeCommunity={}
        for i,c in enumerate(self.comm):
            for node in c:
                nodeCommunity[node]=i
        return nodeCommunity

    def getEntropy(self):
        """Calculate entropy.

        Assumes that the sets in the family do not overlap.
        """
        len_c = map(len, self.comm)
        return ith.entropy_X(np.array(len_c)/float(sum(len_c)))

    def getMutualInformation(self,otherFamily):
        i=0.0
        #n_ij=[]
        #n_i=map(len,list(self))
        #n_j=map(len(list(otherFamily)))
        n=float(sum(map(len,list(self))))
        for c in self:
            n_i=float(len(c))
            for c2 in otherFamily:
                n_j=float(len(c2))
                n_ij=float(len(c.intersection(c2)))
                if n_ij!=0:
                    i+=n_ij/n*log(n_ij*n/n_i/n_j,2)
        return i

    def getNormalizedMutualInformation(self,otherFamily):
        """Return normalized mutual information.

        The normalized mutual information is
             I_n(X;Y) = 2*I(X;Y)/(H(X)+H(Y))
        I_n(X;Y) is always in [0, 1].
        """
        return (2*self.getMutualInformation(otherFamily)
                /(self.getEntropy()+otherFamily.getEntropy()))

    def getMImetric(self,otherFamily):
        """Return a metric based on mutual information.

        The returned value is
             D(X,Y) = 1 - I(X;Y)/max{H(X), H(Y)}
        D(X,Y) is a metric: it is symmetric, non-negative, satisfies
        the triangle inequality and D(X,Y)=0 if and only if X==Y.
        """
        return 1.0 - (self.getMutualInformation(otherFamily)
                      /max(self.getEntropy(),otherFamily.getEntropy()))
        
        
    def getMaxVariationOfInformation(self, otherFamily, N_nodes=None):
        """Return maximum variation of information.

        The maximum variation of information can be used to compare
        two families with overlapping node set.

        The definition comes from Appendix B of
          Andrea Lancichinetti, Santo Fortunato, Janos Kertesz (2009)
          `Detecting the overlapping and hierarchical community
          structure of complex networks'.

        Parameters
        ----------
        otherFamily : NodeFamily object
           The other community sructure to compare with.
        N_nodes : int
           The total number of nodes in all communities. If None, the
           size of the union of all communities in both community
           structures is used. Note that if there are nodes that do
           not belong in any community this will not give the correct
           answer.

        Return
        ------
        N : float
           The maximum variation of information.

        Notes
        -----
        If one community structure consists of only one community
        covering all nodes, this measure is always 0.5 (unless of
        course the other one is identical, in which case 1.0 is
        returned.)
        """

        def p_log2_p(p):
            return (0.0 if p == 0 else -p*np.log2(p))

        # Find out the number of nodes if not given. `Nf` is defined
        # just to make the code more readable.
        if N_nodes is None:
            N_nodes = len(set(reduce(set.union, self.comm+otherFamily.comm)))
        Nf = float(N_nodes)

        ret_val = 1.0
        for XF, YF in [(self, otherFamily), (otherFamily, self)]:
            H_norm = []
            for X_k in XF:
                # Calculate the entropies H(X_k|Y_l) for all Y_l in YF
                # and find the minimum. H_min is initialized to H(X_k).
                px = len(X_k)/Nf
                H_min = H_X = ith.entropy_X([px, 1-px])
                for Y_l in YF:
                    py = len(Y_l)/Nf
                    H_Y = ith.entropy_X([py, 1-py])
                    cut_size = len(X_k.intersection(Y_l))
                    hP_same = (p_log2_p(cut_size/Nf)
                               + p_log2_p((Nf - len(X_k.union(Y_l)))/Nf))
                    hP_diff = (p_log2_p((len(X_k) - cut_size)/Nf)
                               + p_log2_p((len(Y_l) - cut_size)/Nf))
                    if (hP_same > hP_diff):
                        H_min = min(H_min, hP_same + hP_diff - H_Y)

                    #print (X_k, Y_l, hP_same, hP_diff, hP_same > hP_diff,
                    #       (hP_same + hP_diff - H_Y)/H_X)
                H_norm.append((0 if H_X == 0 else H_min/H_X))

            ret_val -= 0.5*sum(H_norm)/len(XF)
            #print H_norm, sum(H_norm)/len(XF)

        return ret_val

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
        #self.multiplier=10**ceil(log(len(cslist))/log(10))
        
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
