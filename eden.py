""" Eden module for network toolbox
This module contains Eden specific classes.

"""

import pynet,random,netext
import communities
from communities import communityTree
from math import sin,cos,asin,sqrt,pi
import math
import numpy


def loadNet_microsatellite(input,removeClones=True,distance="lm"):
    """
    Reads microsatellite data as full net from iterable object
    containing strings (opened file). Look eden.MicrosatelliteData for
    the format the data is read. This function also removes the clones by default.
    """
    msData=MicrosatelliteData(input)
    if removeClones:
        msData=msData.getUniqueSubset()
    msNet=msData.getDistanceMatrix(distance)
    return msNet

class MicrosatelliteData:
    """ A class for parsing and using microsatellite data
    """
    def __init__(self,input):
        """
        The microsatellite data must be given as a input where each row
        has microsatellites for one node/specimen. Alleles should be given as
        integer numbers representing the number of repetitions. The data should have
        even number of columns where each pair represents two homologous alleles.
        Input variable should contain iterable object that outputs the row as a string
        at each iteration step: for example open('msfile.txt').
        """
	lastNumberOfFields=None
        self.alleles=[]
        for lineNumber,line in enumerate(input):
            fields=line.split()
            if len(fields)%2!=0:
                raise SyntaxError("Input should have even number of columns");
	    elif lastNumberOfFields!=None and lastNumberOfFields!=len(fields):
		raise SyntaxError("The input has unconsistent number of columns")
            else:
                fields=map(int,fields)
                if len(self.alleles)==0: #first time here                    
                    for dummy in range(0,len(fields)/2):
                        self.alleles.append([])
                for i in range(0,len(fields),2):                    
                    #you could also sort the alleles here:
                    if fields[i]>fields[i+1]:
                        #print lineNumber #for debug
                        #print line
                        fields[i],fields[i+1]=fields[i+1],fields[i]
                    self.alleles[i/2].append((fields[i],fields[i+1]))

    def getNode(self,index):
        """
        Returns a list of alleles where every two alleles in the same loci
        are coupled together with a tuple object.
        """
        node=[]
        for allele in self.alleles:
            node.append(allele[index])
        return tuple(node)

    def getLocusforNodeIndex(self, locus, node):
        return self.alleles[locus][node]

    def getNumberofLoci(self):
        return len(self.alleles)

    def getMSDistance_hybrid(self,x,y,lm_w=None,nsa_w=None):
        if lm_w==None:
            lm_w=self.lm_w
        if nsa_w==None:
            nsa_w=self.nsa_w
        #distance=0
        #for locus in range(0,len(x)):
        #    distance+=nsa_w[locus]*(len(set([x[locus][0],x[locus][1]]).union(set([y[locus][0],y[locus][1]])))-len(set([x[locus][0],x[locus][1]]).intersection(set([y[locus][0],y[locus][1]]))))
        #    #distance+=nsa_w[locus]*(2-len(set([x[locus][0],x[locus][1]]).intersection(set([y[locus][0],y[locus][1]]))))
        #    distance+=lm_w[locus]*math.sqrt(abs(x[locus][0]-y[locus][0])+abs(x[locus][1]-y[locus][1]))
        #return float(distance)
        return float(sum(self.getMSDistance_vectorHybrid(x,y,lm_w=lm_w,nsa_w=nsa_w)))

    def getMSDistance_vectorHybrid(self,x,y,lm_w=None,nsa_w=None):
        if lm_w==None:
            lm_w=self.lm_w
        if nsa_w==None:
            nsa_w=self.nsa_w
            distance=numpy.zeros(len(x))
        #for locus in range(0,len(x)):
        #    d=0
        #    distance[locus]+=nsa_w[locus]*(len(set([x[locus][0],x[locus][1]]).union(set([y[locus][0],y[locus][1]])))-len(set([x[locus][0],x[locus][1]]).intersection(set([y[locus][0],y[locus][1]]))))
        #    #distance+=nsa_w[locus]*(2-len(set([x[locus][0],x[locus][1]]).intersection(set([y[locus][0],y[locus][1]]))))
        #    distance[locus]+=lm_w[locus]*math.sqrt(abs(x[locus][0]-y[locus][0])+abs(x[locus][1]-y[locus][1]))
        #return distance
        return nsa_w*self.getMSDistance_vectorNonsharedAlleles(x,y)+lm_w*self.getMSDistance_vectorLinearManhattan(x,y)

    def getMSDistance_nonsharedAlleles(self,x,y):
        #distance=0
        #for locus in range(0,len(x)):
        #    distance+=(len(set([x[locus][0],x[locus][1]]).union(set([y[locus][0],y[locus][1]])))-len(set([x[locus][0],x[locus][1]]).intersection(set([y[locus][0],y[locus][1]]))))
        #    #distance+=2-len(set([x[locus][0],x[locus][1]]).intersection(set([y[locus][0],y[locus][1]])))
        #return float(distance)
        return float(sum(self.getMSDistance_vectorNonsharedAlleles(x,y)))/float(len(x))

    def getGroupwiseDistance_DyerNason(self,x,y):
        """
        Returns the distance between two populations defined by Dyer and Nason in:
        "Population graphs: The graph theoretic shape of genetic structure, Mol Ecol
        13:1713-1727 (2004)". This implementation is coded by following: 
        "M.A. Fortuna et al.: Networks of spatial genetic variation across species, PNAS
        vol. 106 no. 45 pp. 19044-19049 (2009)".

        Parameters
        ----------
        x and y are lists of sample indices correspoding to samples of two populations.
        The distance between these populations is calculated.
        """
        #calculate the centroid multivariate coding vector:
        x_cod={} # the codification vector for population x
        for nodeIndex in x:
            for locus in range(self.getNumberofLoci()):
                alleles=self.getLocusforNodeIndex(locus,nodeIndex)
                key=(locus,alleles[0])
                x_cod[key]+=x_cod.get(key,0)+1
                key=(locus,alleles[1])
                x_cod[key]+=x_cod.get(key,0)+1
        for key in x_cod.keys(): #normalize
            x_cod[key]=x_cod[key]/float(len(x))

                
        raise NotImplementedError()

    def getGroupwiseDistance_Goldstein(self,x,y):
        """
        Returns the goldstein distance between two populations

        Parameters
        ----------
        x and y are lists of sample indices correspoding to samples of two populations.
        The distance between these populations is calculated.

        Example
        -------
        >>> ms=eden.MicrosatelliteData(open("../data/microsatellites/microsatellites.txt",'r'))
        >>> ms_u = ms.getUniqueSubset()
        >>> ms_u.getGroupwiseDistance_Goldstein([1,2,3,4],[1,2,3,4]) == 1330.5
        True
        """
        
        distList = []
        for locus in range(self.getNumberofLoci()):
            
            # calculates allele frequences
            xdict = {}
            for nodeIndex in x:
                xlocus = self.getLocusforNodeIndex(locus,nodeIndex)
                xdict[xlocus[0]] = xdict.get(xlocus[0],0) + 1
                xdict[xlocus[1]] = xdict.get(xlocus[1],0) + 1                
                    
            ydict = {}
            for nodeIndex in y:
                ylocus = self.getLocusforNodeIndex(locus,nodeIndex)
                ydict[ylocus[0]] = ydict.get(ylocus[0],0) + 1 
                ydict[ylocus[1]] = ydict.get(ylocus[1],0) + 1

            # calculates goldstain distance
            dist = 0
            for i in xdict:
                for j in ydict:
                    dist += 1.0*(i-j)**2*xdict[i]/(2*len(x))*ydict[j]/(2*len(y))/self.getNumberofLoci()

            distList.append(dist)

        return sum(distList)

    def getGroupwiseDistanceMatrix(self,groups,distance='goldstein'):
        """
        Returns a distance matrix in form of a full network (pynet.SymmFullNet). The groups
        argument must be an iterable object where each element is also iterable object containing
        the indices of the nodes belonging to each group.
        """
        #only distance measure implemented so far:
        getGroupwiseDistance=self.getGroupwiseDistance_Goldstein
        
        grouplist=list(groups)
        ngroups=len(grouplist)
        matrix=pynet.SymmFullNet(ngroups)
        for i in range(0,ngroups):
            for j in range(i+1,ngroups):
                matrix[i,j]=getGroupwiseDistance(grouplist[i],grouplist[j])
        return matrix   

    def getMSDistance_linearManhattan(self,x,y):
        """
        Returns the distance between two nodes/specimen
        """
        #distance=0
        #for locus in range(0,len(x)):
        #    distance+=math.sqrt(abs(x[locus][0]-y[locus][0])+abs(x[locus][1]-y[locus][1]))
        #return float(distance)/float(len(x))
        return float(sum(self.getMSDistance_vectorLinearManhattan(x,y)))/float(len(x))

    def getMSDistance_vectorLinearManhattan(self,x,y):
        distance=numpy.zeros(len(x))
        for locus in range(0,len(x)):
            distance[locus]=abs(x[locus][0]-y[locus][0])+abs(x[locus][1]-y[locus][1])
        return distance

    def getMSDistance_vectorNonsharedAlleles_old(self,x,y):
        distance=numpy.zeros(len(x))
        for locus in range(0,len(x)):
            distance[locus]=len(set([x[locus][0],x[locus][1]]).union(set([y[locus][0],y[locus][1]])))-len(set([x[locus][0],x[locus][1]]).intersection(set([y[locus][0],y[locus][1]])))
        return distance


    def getMSDistance_vectorNonsharedAlleles(self,x,y):
        return self.getMSDistance_vector(x,y,self.getMSDistance_singleLocus_NonsharedAlleles)
       

    def getMSDistance_singleLocus_NonsharedAlleles(self,x,y):
        alleles=x+y
        distance=0
        for allele in alleles:
            if allele not in x or allele not in y:
                distance+=1
        return distance
            
    def getMSDistance_vector(self,x,y,distance_singleLocus):
        distance=numpy.zeros(len(x))
        for locus in range(0,len(x)):
            distance[locus]=distance_singleLocus(x[locus],y[locus])
        return distance

    def getMSDistance_singleLocus_AlleleParsimony(self,x,y):
        first=len(set([x[0],y[0]]))+len(set([x[1],y[1]]))
        second=len(set([x[0],y[1]]))+len(set([x[1],y[0]]))
        return float(min([first,second]))-2.0

    def getMSDistance_vectorAlleleParsimony(self,x,y):
        return self.getMSDistance_vector(x,y,self.getMSDistance_singleLocus_AlleleParsimony)

    def getMSDistance_alleleParsimony(self,x,y):
        return float(sum(self.getMSDistance_vectorAlleleParsimony(x,y)))/float(len(x))

    
    def getDistanceMatrix(self,distance="lm",nodeNames=None):
        """
        Computes the distance between each node and returns the corresponding
        distance matrix.
        """
        if distance=="lm":
            getMSDistance=self.getMSDistance_linearManhattan
        elif distance=="nsa":
            getMSDistance=self.getMSDistance_nonsharedAlleles
        elif distance=="ap":
            getMSDistance=self.getMSDistance_alleleParsimony
        elif distance=="hybrid":
            getMSDistance=self.getMSDistance_hybrid
        else: #default
            getMSDistance=self.getMSDistance_linearManhattan
            
        numberOfSpecimens=len(self.alleles[0])
        matrix=pynet.SymmFullNet(numberOfSpecimens)
        if nodeNames==None:
            nodeNames=range(0,numberOfSpecimens)
        for i,iName in enumerate(nodeNames):
            for j,jName in enumerate(nodeNames[i+1:]):
                matrix[iName,jName]=getMSDistance(self.getNode(i),self.getNode(j))
        return matrix
            
    def getSubset(self,nodes):
        """
        Returns a new MicrosatelliteData object containing only nodes given
        as a input. The input is a list of indices of the nodes.
        """
        newData=MicrosatelliteData([])
        for allele in self.alleles:
            newAllele=[]
            for node in nodes:
                newAllele.append(allele[node])
            newData.alleles.append(newAllele)
        return newData

    def randomize(self,full=False):
        """
        Shuffles the homologous alleles in the whole dataset
        """
        if full:
            for j,allele in enumerate(self.alleles):
                newAlleles=[]
                alleleList=[]
                for apair in allele:
                    alleleList.append(apair[0])
                    alleleList.append(apair[1])
                random.shuffle(alleleList)
                for i in range(0,len(alleleList),2):
                    newAlleles.append((alleleList[i],alleleList[i+1]))
                self.alleles[j]=newAlleles

        #this really should shuffle all the homologous alleles
        #and not small and large alleles separately
        else:
            for allele in self.alleles:
                random.shuffle(allele)

    def getNumberOfNodes(self):
        return len(self.alleles[0])
    
    def getUniqueSubset(self,returnOldIndices=False):
        """
        Returns a new MicrosatelliteData object with all identical nodes
        removed except the first occurances of them.
        """
        numberOfNodes=self.getNumberOfNodes()
        nodeSet=set()
        uniqueNodes=[]
        for i in range(0,numberOfNodes):
            node=self.getNode(i)
            if node not in nodeSet:
                nodeSet.add(node)
                uniqueNodes.append(i)
                #print i+1 #indices for Jenni and Jari
        if returnOldIndices:
            return (self.getSubset(uniqueNodes),uniqueNodes)
        else:
            return self.getSubset(uniqueNodes)

    def __str__(self):
        theStr=""
        for nodeIndex in range(self.getNumberOfNodes()):
            node=self.getNode(nodeIndex)
            alleleList=reduce(lambda x,y:x+y,node)
            alleleStr=reduce(lambda x,y:str(x)+" "+str(y),alleleList)
            theStr+=alleleStr+"\n"
        return theStr

class LocationData:
    def __init__(self,dir="../data/distancematrix_and_locations/"):
        self.location=list(open(dir+"locations.txt"))
        self.name=list(open(dir+"location_names.txt"))
        self.latlong=list(open(dir+"location_coords_latlong.txt"))
        self.c=list(open(dir+"location_classes.txt"))

        #parse latlong:
        newll=[]
        for llstring in self.latlong:
            ll=map(float,llstring.strip().split())
            assert len(ll)==2
            newll.append(ll)
        self.latlong=newll

    def getLocation(self,node):
        return int(self.location[node])

    def getClass(self,node):
        return int(self.c[self.getLocation(node)-1])

    def getName(self,node):
        return self.name[self.getLocation(node)-1]

    def getLatlong(self,node):
        return self.latlong[self.getLocation(node)-1]
        
    def getClassHist(self,nodes):
        locations=map(self.getClass,nodes)
        h=[0,0,0]
        for l in locations:
            h[l-1]=h[l-1]+1;
        return h

    def getClassSets(self,nodes):
        """
        Returns a NodeFamily of the node classes 
        """
        cmap={1:[],2:[],3:[]}
        for node in nodes:
            cmap[self.getClass(node)].append(node)
        return communities.NodeFamily(cmap)

    def getLocationSets(self,nodes):
        """
        Returns a NodeFamily of the node classes 
        """

        cmap={}
        for ln in range(1,len(self.name)+1):
            cmap[ln]=[]
        for node in nodes:
            cmap[self.getLocation(node)].append(node)
        return communities.NodeFamily(cmap)
            
    def getNodesAtLocation(self,location):
        """
        Returns all node indices at the given location index.
        """
        nodes=[]
        for node,nodeLocation in enumerate(self.location):
            if location==int(nodeLocation):
                nodes.append(node)
        return nodes

    def getClassByLocation(self,location):
        """
        Returns class index for the given location.
        """
        if location<1:
            raise ValueError("Invalid location index: " +str(location))
        return int(self.c[location-1])

    def getLatlongByLocation(self,location):
        if location<1:
            raise ValueError("Invalid location index: " +str(location))        
        return self.latlong[location-1]

    def getLocations(self):
        """
        Returns the location indices.
        """
        #return map(lambda x:int(x),self.location)
        return map(lambda x:x+1,range(len(self.name)))

    def getGeoDistMatrix(self,locations=None):
        """
        Returns the matrix of distances between the locations in this object. Locations can be
        speciefied as a list of locations for between which the distance is to be calculated.
        """        
        if locations==None:
            locations=self.getLocations()
        matrix=numpy.zeros([len(locations),len(locations)])
        for i in range(len(locations)):
            for j in range(len(locations)):
                matrix[i,j]=self.getGeoDistByLocation(locations[i],locations[j],lookuptable=False)
        return matrix
    
    def getGeoDistByLocation(self,l1,l2,lookuptable=True):
        if lookuptable:
            if not hasattr(self,"geotable_location"):
                self.geotable=-1*numpy.ones([len(self.latlong),len(self.latlong)])
            d=self.geotable[l1-1,l2-1]
            if d!=-1:
                return d

        #based on code by Jari
        #formula used:   Haversine Formula (from R.W. Sinnott, "Virtues of the Haversine",
        #Sky and Telescope, vol. 68, no. 2, 1984, p. 159):
        #URL: http://www.faqs.org/faqs/geography/infosystems-faq/

        c=(pi/180)
        R=6371000
        ll1=self.getLatlongByLocation(l1)
        ll2=self.getLatlongByLocation(l2)
        lat1,lon1,lat2,lon2=c*ll1[0],c*ll1[1],c*ll2[0],c*ll2[1]

        dlon=lon2-lon1
        dlat=lat2-lat1
        a=pow(sin(dlat/2),2)+cos(lat1)*cos(lat2)*pow(sin(dlon/2),2)
        c=2*asin(min(1,sqrt(a)))
        d=R*c

        if lookuptable:
            self.geotable[l1-1,l2-1]=d
        return d

    def getGeoDist(self,node1,node2,lookuptable=True):
        """
        Calculates the geographic distance of two nodes.
        """
        return self.getGeoDistByLocation(self.getLocation(node1),self.getLocation(node2),lookuptable)
            
class ClassTree(communities.communityTree):
    def getNodeClasses(self,locationData):
        classes={}
        self.cslist.reverse()
        for level in range(0,len(self.cslist)):
            for communityIndex in range(0,len(self.cslist[level])):
                classHist=locationData.getClassHist(self.cslist[level][communityIndex])
                classString=reduce(lambda x,y:str(x)+","+str(y),classHist)
                classes[self._getNameByNode((level,communityIndex))]=classString
        self.cslist.reverse()
        return classes

    def getNodeColors(self,locationData):
        cstrings=self.getNodeClasses(locationData)
        colors={}
        for node in cstrings.keys():            
            c=map(int,cstrings[node].split(','))
            if c[0]>c[1] and c[0]>c[2]:
                color="999900" #yellow
            elif c[1]>c[0] and c[1]>c[2]:
                color="000099" #blue
            else:
                color="990000" #red
            colors[node]=color
        return colors

    def getNodeHist(self,locationData):
        cstrings=self.getNodeClasses(locationData)
        nodeHist={}
        for node in cstrings.keys():            
            c=map(int,cstrings[node].split(','))
            nodeHist[node]=c
        return nodeHist
