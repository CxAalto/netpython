import _cnet

def clusteringCoefficent(net,node):
    if not net.isNumeric():
        node=net._nodes[node]

    return _cnet.clusteringCoefficient(net._net,node)
