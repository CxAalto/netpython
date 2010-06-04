import pynet,netext
import numpy as np

def makeER(n,p):
    """
    Make a realisation of Erdos-Renyi network
    * fast for non-sparse networks
    * the sparce version should be implemented
    """
    net=pynet.SymmNet()
    for i in range(0,n):
        for j in range(0,i):
            if p > np.random.ranf():
                net[i,j]=1
    return net
