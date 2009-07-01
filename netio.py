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

#   LIST OF CHANGES 
# 1.7. RT
#   - fixed loadNodeProperties such that decimal numbers are
#     interpreted as floats, not strings (it's still a hack
#     though... and it cannot handle exponential notation, for example)
#   - modified function isanum and added function isint that can
#     handle negative numbers too
#   - earlier, if the node property file contained nodes that are not
#     present in the network, the function was aborted; now only a
#     warning is issued.
# 30.06.RT - modified loadNodeProperties such that the property file does not need
#            to have headers. Now, each property name can be given as an argument.
# 24.06.JS fixed loadNodeProperties (nodelabels to int if numbers)
# 24.06.JS fixed & documented loadNodeProperties (checks if input file node exists in the network)


import pynet,netext,warnings

from matplotlib.mlab import norm
knownFiletypes=["edg","gml","mat","net"]

def getFiletype(filename):
    """
    Gets filename as input and returns its type
    """
    sfn=filename.split('.')
    filetype=sfn[len(sfn)-1]
    return filetype



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
        nodeNameToIndex[node]=index+1

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
    
def loadNodeProperties(net,filename,splitterChar=None,propertyNames=None):
    """Reads metadata (properties for nodes) from a file. Usage:
    loadNodeProperties(net,filename,splitterChar=None,propertyNames=None).
    The metadata file can contain any number of columns. The first column
    should contain names of nodes contained in 'net', and the other
    columns contain user-defined properties.
    
    If a list 'propertyNames' is not given, the first row must
    contain headers. The first column header should be node_label,
    and the other column headers are names of the user-defined properties.
    They are automatically appended to the property list in 'net'.
    Alternatively, you can provide a list 'propertyNames' containing
    a label for each column. In this case, your file should not
    contain a header. The function 'loadNodeProperties' checks whether
    'propertyNames' contains 'node_label' as the first element, and adds
    it if it doesn't, so you do not need to give it explicitly. 

    Example input file format:
    node_label node_color node_class
    node1      blue       class1
    """

    #todo: see if the node names are strings, ints or floats [DONE/JS/2605]
    # loadNet converts numerical node labels to ints, has been taken into account here.
    #todo: check if node is in the network [DONE/JS/2705]

    #todo: how to deal with FullNets???[DONE|JS/2705]
    #todo: check that there are no non-existing nodes/too many input lines [DONE|JS/2705]

    #todo: write a check that all nodes get properties!!!

    #tested for i) SymmNet with string node labels, ii) -"- with integer labels,
    # iii) FullNet, iv) the above cases with too many lines / non-existing nodes
    # in input metadata file

    def isanum(str):

        # checks if a string contains only digits, decimal points "." or minus signs "-"
        
        from string import digits
        for c in str:
            if not c in digits and c!="." and c!="-": return 0
        return 1


    def isint(str):

        # checks if a string contains only digits or minus signs "-"
        
        from string import digits
        for c in str:
            if not c in digits and c!="-": return 0
        return 1

    
    f=open(filename,'rU')   # NOTE: the 'U' flag means "Universal Newlines" - guarantees that
                            # newlines are recognized as newlines independent of exact EOL character
                            # and operating system. USE THIS EVERYWHERE FROM NOW ON
    

    #Read in the fields
    line=f.readline()
    
    if propertyNames==None: 
        fieldNames=line.strip().split(splitterChar)  # field names are taken from first line (header)
        nfields=len(fieldNames)
    else:
        fieldNames=propertyNames    # fieldNames are given
        if type(fieldNames)==str:
            fieldNames=[fieldNames] # if only a single field name string was given, convert it into a list (this makes it easier for the user if only one property is added, as he only needs to type 'property' and not ['property'] )
        if fieldNames[0]=="node_label":  # the first element is node_label
            nfields=len(fieldNames)
        else:
            fieldNames=["node_label"]+ fieldNames[:]  # if the first element is NOT node_label, add it
            nfields=len(fieldNames)
            
    #if not(net.isFull()):
    # SymmNet has no module isFull, so I replaced the test with checking whether the net is one of the Full types.
    if type(net)!=pynet.FullNet and type(net)!=pynet.SymmFullNet:

        # for "ordinary" networks, node properties are "matched" based on first column of
        # input file, containing node labels
    
        if fieldNames[0]!="node_label":
            raise Exception("The properties file should define the first field as \"node_label\".")

        #Add the property names to the net
        for field in range(1,nfields):
            netext.addNodeProperty(net,fieldNames[field])


        #Add the properties for each node
        someNodesNotInNetwork=False
        for i,line in enumerate(f):
        
            fields=line.strip().split(splitterChar)
        
            if len(fields)!=nfields:
                raise Exception("The number of fields on a row does not match the header line or given list of properties: "+str(i+2))
        
            if isint(fields[0]):
                nodeName=int(fields[0]) # if node name/label is an integer, convert to int
            else:
                nodeName=fields[0]


            if nodeName in net:
                for field in range(1,nfields):
                    tmp=fields[field]
                    if isanum(tmp):  # if it is a number 
                        net.nodeProperty[fieldNames[field]][nodeName]=float(tmp)
                        if isint(tmp):  # if it is integer 
                            net.nodeProperty[fieldNames[field]][nodeName]=int(tmp)
                    else: # if it is a string
                        net.nodeProperty[fieldNames[field]][nodeName]=tmp 

            else:
                someNodesNotInNetwork=True
                #warnings.warn("Node \'"+str(nodeName)+"\' in input file doesn't exist in the network!")


        if someNodesNotInNetwork:
            warnings.warn("Some of the nodes in the property file do not exist in the network!")
            
    else:

        netsize=len(net)

        # for FullNets and SymmFullNets, where nodes are just indexed (0..(N-1)), properties are
        # added to nodes in this order.
        #
        # if node_labels are used, these will be inserted as regular property fields   
        #
        # todo: check that input file has N-1 rows

        for field in range(0,nfields):

            netext.addNodeProperty(net,fieldNames[field])

        #Add the properties for each node
        for i,line in enumerate(f):
        
            fields=line.strip().split(splitterChar)
        
            if len(fields)!=nfields:
                raise Exception("Invalid number of fields on row: "+str(i+2))

            if i<netsize:
            
                for field in range(0,nfields):
                    net.nodeProperty[fieldNames[field]][(i)]=fields[field]

            else:

                raise Exception("Too many lines, network size is "+str(netsize))

        


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


