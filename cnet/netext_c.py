import _cnet

def getNumberOfTriangles(net):
    return _cnet.getNumberOfTriangles(net._net)

def clusteringCoefficent(net,node):
    #if not net.isNumeric():
    node=net._nodes[node]

    return _cnet.clusteringCoefficient(net._net,node)

def getMeanPathLength(net,maxSamples=1000):
    return _cnet.meanPathLength(net._net,maxSamples)
