import _cnet

def shuffleEdges(net,rounds,limit,randseed):
    return _cnet.shuffleEdges(net._net,rounds,limit,randseed)

#def confModelSimple(net,rounds,randseed):
#    return _cnet.confModelSimple(net._net,rounds,randseed)
