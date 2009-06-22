"""Input and output functions for pynet
  
  Current status
  --------------
  This module contains functions for reading and writing files containing networks.
  loadNet and writeNet are general functions for loading and writing networks in 
  different file types. This means that they try to recognize the filetype of the
  network file from the filename and then use appropriate function to read/write it.

  The user can also use loadNet_[format] and writeNet_[format] directly to force 
  loading or writing to be done in given format.

  Currently only the edg, gml and matrix format has been implemented 

  Future additions
  ----------------
  *Important: make loadNet_? work as loadNet, so that no that filename is input
  *Support for metadata in network files
  *graphXML-format and others
  *make gml-io stable
"""
import pynet,netext
#from eden import MicrosatelliteData
from matplotlib.mlab import norm
knownFiletypes=["edg","gml","mat","net"]

def getFiletype(filename):
    """
    Gets filename as input and returns its type
    """
    sfn=filename.split('.')
    filetype=sfn[len(sfn)-1]
    return filetype

#def loadNet_microsatellite(input,removeClones=True):
#    """
#    Reads microsatellite data as full net from iterable object
#    containing strings (opened file). Look eden.MicrosatelliteData for
#    the format the data is read. This function also removes the clones by default.
#    """
#    msData=MicrosatelliteData(input)
#    if removeClones:
#        msData=msData.getUniqueSubset()
#    msNet=msData.getDistanceMatrix()
#    return msNet

def loadNet_gml(input):
    """
    Reads a networks data from input in gml format.

    Note: This is not a complete gml-parser, because gml format can
    hold almost anykind of data. Instead this parser tries to find
    edges of one graph from the given input. Use at you own risk with
    complicated gml-files.
    """

    source=None
    target=None
    value=None
    for line in input:
        line=line.strip()
        if line.startswith("directed"):
            if line[9:10]=="0":
                net=pynet.SymmNet()
            elif line[9:10]=="1":
                net=pynet.Net()
        elif line.startswith("source"):
            source=line.split()[1]
        elif line.startswith("target"):
            target=line.split()[1]
        elif line.startswith("value"):
            value=line.split()[1]
        elif line.startswith("edge"):
            if source!=None and target!=None:
                if value!=None:
                    net[source][target]=float(value)
                else:
                    net[source][target]=1
                source=None
                target=None
                value=None
    if source!=None and target!=None:
        if value!=None:
            net[source][target]=float(value)
        else:
            net[source][target]=1


    return net

def loadNet_edg(input, mutualEdges = False, splitterChar = None,symmetricNet=True):
    """
    Reads a network data from input in edg format.

    If mutualEdges is set to True, an edge is added between nodes i
    and j only if both edges (i,j) and (j,i) are listed. The weight of
    the edge is the average of the weights of the original edges.
    """
    def isNumerical(input):
	try:
	   for line in input:
		int(line.split(splitterChar)[0])
		int(line.split(splitterChar)[1])
	except ValueError:
	   input.seek(0)
	   return False
	input.seek(0)
	return True

    numerical=isNumerical(input)
	
    if symmetricNet:
        newNet=pynet.SymmNet()
    else:
        newNet=pynet.Net()


    nodeMap = {} # Used only if mutualEdges = True.

    for line in input:
        fields=line.split(splitterChar)
        if len(fields)>2:            
	    if numerical:
		fields[0]=int(fields[0])
		fields[1]=int(fields[1])
            if fields[0]!=fields[1]:
                if mutualEdges:
                    if nodeMap.has_key( (fields[1], fields[0]) ):
                        value = 0.5*( nodeMap[(fields[1], fields[0])] + float(fields[2]) )
                        newNet[fields[0]][fields[1]] = value
                    else:
                        nodeMap[(fields[0], fields[1])] = float(fields[2])
                else:
                    newNet[fields[0]][fields[1]]=float(fields[2])

    return newNet


def loadNet_mat(input, mutualEdges = False, splitterChar = None,symmetricNet=True):
    rows=0
    columns=0
    for line in input:
        rows+=1
        fields=line.split(splitterChar)
        if rows!=1 and len(fields)!=columns:
            raise Exception("Unconsistent number of columns at row "+str(rows))
        columns=len(fields)
    if columns!=rows:
        raise Exception("Not a square matrix: "+str(columns)+" columns and "+str(rows)+" rows.")
    input.seek(0)

    if symmetricNet:
        newNet=pynet.SymmFullNet(columns)
    else:
        newNet=pynet.FullNet(columns)

    row=0
    for line in input:
        fields=line.split(splitterChar)
        for columnIndex in range(0,columns):
            if columnIndex!=row:
                newNet[row,columnIndex]=float(fields[columnIndex])
        row+=1

    return newNet

def loadNet_net(input):
    raise Exception("Reading Pajek file format is not implemented.")

def writeNet_gml(net,filename):
    file=open(filename,'w')
    file.write("graph [\n")
    if net.__class__==pynet.SymmNet:
        file.write("directed 0\n")
    else:
        file.write("directed 1\n")

    nodeIndex=netext.Enumerator()
    for node in net:
        file.write("node [\n")
        file.write("id "+str(nodeIndex[node])+"\n")
        file.write("label "+str(node))
        file.write("]\n")

    for edge in net.edges:
        file.write("edge [\n")
        file.write("source " + str(nodeIndex[edge[0]])+"\n")
        file.write("target " + str(nodeIndex[edge[1]])+"\n")
        file.write("value " + str(edge[2])+"\n")
        file.write("]\n")

    file.write("]\n")

def writeNet_edg(net,filename,headers=False):
    #edges=netext.getEdges(net)
    edges=net.edges
    file=open(filename,'w')
    if headers==True:
        file.write("HEAD\tTAIL\tWEIGHT\n")
    for edge in edges:
        file.write(str(edge[0])+"\t"+str(edge[1])+"\t"+str(edge[2])+"\n")

def writeNet_net(net,filename):
    """
    Write network files in Pajek format.

    Todo: add writing metadata to the vertices rows
    """
    file=open(filename,'w')

    #Writing vertices to the disk.
    numberOfNodes=len(net)
    nodeNameToIndex={}
    file.write("*Vertices "+str(numberOfNodes)+"\n")
    for index,node in enumerate(net):
        file.write(str(index+1)+" "+str(node)+"\n")
        nodeNameToIndex[node]=index

    #Writing edges to the disk
    file.write("*Arcs\n")
    if net.isSymmetric():
        file.write("*Edges\n")
    for edge in net.edges:
        file.write(str(nodeNameToIndex[edge[0]])+"\t"+str(nodeNameToIndex[edge[1]])+"\t"+str(edge[2])+"\n")
    if not net.isSymmetric():
        file.write("*Edges\n")

    del nodeNameToIndex


def writeNet_mat(net,filename):
    file=open(filename,'w')
    nodes=list(net)
    for i in nodes:
        first=True
        for j in nodes:
            if first:
                first=False
            else:
                file.write(" ")
            file.write(str(net[i,j]))
        file.write("\n")
    file.close()
    return nodes



def writeNet(net,filename,headers=False):
    filetype=getFiletype(filename)
    if filetype=='edg':
        writeNet_edg(net,filename,headers)
    elif filetype=='gml':
        writeNet_gml(net,filename)
    elif filetype=='mat':
        writeNet_mat(net,filename)
    elif filetype=='net':
        writeNet_net(net,filename)
    else:
        print "Unknown filetype, use writeNet_[filetype]"


def loadNet(filename, mutualEdges = False, splitterChar = None,symmetricNet=True):
    inputfile=open(filename)
    filetype=getFiletype(filename)
    if filetype=='edg':
        newNet=loadNet_edg(inputfile, mutualEdges, splitterChar,symmetricNet)
    elif filetype=='gml':
        newNet=loadNet_gml(inputfile)
    elif filetype=='mat':
        newNet=loadNet_mat(inputfile)
    elif filetype=='net':
        newNet=loadNet_net(inputfile)
    else:
        print "Unknown filetype, use loadNet_[filetype]"
    inputfile.close()
    return newNet
    


def loadNodeProperties(net,filename,splitterChar=None):
    #todo: see if the node names are strings, ints or floats
    f=open(filename,'r')

    #Read in the fields
    line=f.readline()
    fieldNames=line.strip().split(splitterChar)
    nfields=len(fieldNames)
    if fieldNames[0]!="name":
        raise Exception("The properties file should define the first field as \"name\".")

    #Add the property names to the net
    for field in range(1,nfields):
        netext.addNodeProperty(net,fieldNames[field])

    #Add the properties for each node
    for i,line in enumerate(f):
        fields=line.strip().split(splitterChar)
        if len(fields)!=nfields:
            raise Exception("Invalid number of fields on row: "+str(i+2))
        nodeName=fields[0] #todo: see if node is in net
        for field in range(1,nfields):
            net.nodeProperty[fieldNames[field]][nodeName]=fields[field]

def saveNodeProperties(net,filename):
    plist=list(net.nodeProperty)
    f=open(filename,'w')

    #Write headers
    f.write("name")
    for p in plist:
        f.write(" "+p)
    f.write("\n")

    #Write values
    for node in net:
        f.write(str(node))
        for p in plist:
            f.write(" "+str(net.nodeProperty[p][node]))
        f.write("\n")


