"""Input and output functions for pynet
  
  Current status
  --------------
  This module contains functions for reading and writing files
  containing networks.  loadNet and writeNet are general functions for
  loading and writing networks in different file types. This means
  that they try to recognize the filetype of the network file from the
  filename and then use appropriate function to read/write it.

  The user can also use loadNet_[format] and writeNet_[format]
  directly to force loading or writing to be done in given format.

  Currently only the edg, gml and matrix format has been implemented 

  Future additions
  ----------------
  - Important: make loadNet_? work as loadNet, so that no that
    filename is input
  - Support for metadata in network files
  - graphXML-format and others
  - make gml-io stable
"""

import pynet,netext,warnings
import sys
knownFiletypes=["edg","gml","mat","net"]

def getFiletype(fileName):
    """Infer the type of a file.

    (Current behaviour is to just return the file name suffix after
    the last dot in fileName.)

    Parameters
    ----------
    filename : string
        The filename whose type you want to know.

    Return
    ------
    filetype : string
        A string literal depicting the file type.
    """

    # Return the file identifier after the last dot.
    # Examples: mynet.edg     ==>   edg
    #           mynet.old.mat ==>   mat
    return fileName.split('.')[-1]


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

def loadNet_edg(input, mutualEdges=False, splitterChar=None, symmetricNet=True,
                numerical=None):
    """Read network data from input in edg format.

    If `mutualEdges` is set to True, an edge is added between nodes i
    and j only if both edges (i,j) and (j,i) are listed. The weight of
    the edge is the average of the weights of the original edges.

    If `mutualEdges` is False and the same edge is encountered
    multiple times, the edge weight will be the sum of all weights.
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

    if numerical is None:
        numerical = isNumerical(input)
    
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
                        value = 0.5*( nodeMap[(fields[1], fields[0])] 
                                      + float(fields[2]) )
                        newNet[fields[0]][fields[1]] = value
                    else:
                        nodeMap[(fields[0], fields[1])] = float(fields[2])
                else:
                    newNet[fields[0]][fields[1]] += float(fields[2])

    return newNet


def loadNet_mat(input, mutualEdges=False, splitterChar=None,symmetricNet=True):
    rows, columns = 0, 0
    for line in input:
        rows += 1
        fields=line.split(splitterChar)
        if rows != 1 and len(fields) != columns:
            raise Exception("Unconsistent number of columns at row %d." % rows)
        columns = len(fields)
    if columns != rows:
        raise Exception("Not a square matrix: %d columns and %d rows."
                        % (columns, rows))
    input.seek(0)

    if symmetricNet:
        newNet=pynet.SymmFullNet(columns)
    else:
        newNet=pynet.FullNet(columns)

    row = 0
    for line in input:
        fields=line.split(splitterChar)
        for columnIndex in range(0,columns):
            if columnIndex != row:
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

def writeNet_edg(net, outputFile, headers=False):
    if not hasattr(outputFile, 'write'):
        raise ValueError("Parameter 'outputFile' must be a file object.")
    #edges=netext.getEdges(net)
    edges=net.edges
    if headers==True:
        outputFile.write("HEAD\tTAIL\tWEIGHT\n")
    for edge in edges:
        outputFile.write("\t".join(map(str, edge)) + "\n")

def writeNet_net(net, outputFile):
    """
    Write network files in Pajek format.

    Todo: add writing metadata to the vertices rows
    """
    if not hasattr(outputFile, 'write'):
        raise ValueError("Parameter 'outputFile' must be a file object.")
        
    #Writing vertices to the disk.
    numberOfNodes = len(net)
    nodeNameToIndex = {}
    outputFile.write("*Vertices "+str(numberOfNodes)+"\n")
    for index,node in enumerate(net):
        outputFile.write(str(index+1)+' "'+str(node)+'"\n')
        nodeNameToIndex[node]=index+1

    #Writing edges to the disk
    outputFile.write("*Edges\n")
    for edge in net.edges:
        outputFile.write(str(nodeNameToIndex[edge[0]]) + "\t" 
                         + str(nodeNameToIndex[edge[1]]) + "\t"
                         + str(edge[2]) + "\n")

    del nodeNameToIndex

def writeNet_mat(net, outputFile):
    if not hasattr(outputFile, 'write'):
        raise ValueError("Parameter 'outputFile' must be a file object.")

    nodes=list(net)
    for i in nodes:
        first=True
        for j in nodes:
            if first:
                first=False
            else:
                outputFile.write(" ")
            outputFile.write(str(net[i,j]))
        outputFile.write("\n")
    return nodes


def writeNet(net, output, headers=False, fileType=None):
    """Write network to disk.

    Parameters
    ----------
    net : pynet network object
        The network to write.
    output : str or file
        Name of the file to be opened.
    headers : bool
        If true, print headers before the actual network data (affects
        only edg format).
    fileType : str
        Type of the output file. In None, the suffix of fileName will
        be used to guess the file type.

    Exceptions
    ----------
    ValueError : If file type is unknown or unable to write to
                 `output`.
    """
    # If `output` is a string, we assume it is a file name and open
    # it. Otherwise if it implements 'write'-method we assume it is a
    # file object.
    fileOpened = False
    if isinstance(output, str):
        outputFile = open(output, 'w')
        fileOpened = True
    elif not hasattr(output, 'write'):
        raise ValueError("'output' must be a string or an object "
                         "with a 'write'-method.")
    else:
        outputFile = output

    try:
        # Infer file type if not explicitely given.
        if fileType is None and hasattr(outputFile, 'name'):
            fileType = getFiletype(outputFile.name)

        # Write out the network.
        if fileType == 'edg':
            writeNet_edg(net, outputFile, headers)
        elif fileType in ('gml', 'mat', 'net'):
            eval("writeNet_%s(net,outputFile)" % fileType)
        else:
            raise ValueError("Unknown file type, try writeNet_[filetype].")
    finally:
        if fileOpened:
            outputFile.close()

def loadNet(input, mutualEdges=False, splitterChar=None, symmetricNet=True,
            numerical=None, fileType=None):
    """Read network from disk.

    Parameters
    ----------
    input : str or file
        Name of the file to be opened or a file object.
    fileType : str
        Type of the output file. In None, the suffix of fileName will
        be used to guess the file type.

    Exceptions
    ----------
    ValueError : If file type is unknown or unable to read from
                 `input`.
    """
    # If `input` is a string, we assume it is a file name and open
    # it. Otherwise if it implements 'write'-method we assume it is a
    # file object.
    fileOpened = False
    if isinstance(input, str):
        inputFile = open(input, 'r')
        fileOpened = True
    elif not isinstance(input, file):
        raise ValueError("'input' must be a string or a file object.")
    else:
        inputFile = input
    
    # Infer file type if not explicitely given.
    if fileType is None and hasattr(inputFile, 'name'):
        fileType = getFiletype(inputFile.name)

    # Read in the network.
    try:
        # edg-files need different behaviour.
        if fileType == 'edg':
            newNet = loadNet_edg(inputFile, mutualEdges, splitterChar,
                                 symmetricNet, numerical)
        elif fileType in ('gml', 'mat', 'net'):
            newNet = eval("loadNet_%s(inputFile)" % fileType)
        else:
            raise ValueError("Unknown file type '%s', try loadNet_[filetype]."
                             % fileType)
    finally:
        if fileOpened:
            inputFile.close()

    return newNet
    
def loadNodeProperties(net,filename,splitterChar=None,propertyNames=None):
    """Read metadata (properties for nodes) from a file.

    Usage:
       loadNodeProperties(net,filename,splitterChar=None,propertyNames=None).

    The metadata file can contain any number of columns. The first
    column should contain names of nodes contained in 'net', and the
    other columns contain user-defined properties.
    
    If a list 'propertyNames' is not given, the first row must contain
    headers. The first column header should be node_label, and the
    other column headers are names of the user-defined properties.
    They are automatically appended to the property list in 'net'.
    Alternatively, you can provide a list 'propertyNames' containing a
    label for each column. In this case, your file should not contain
    a header. The function 'loadNodeProperties' checks whether
    'propertyNames' contains 'node_label' as the first element, and
    adds it if it doesn't, so you do not need to give it explicitly.

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
    
    if propertyNames==None:
        line=f.readline() 
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
                raise Exception("The number of fields on a row does not match"
                                " the header line or given list of properties: "
                                +str(i+2))
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


