import pynet,netext

def makeER(n,p):
    """
    Make a realisation of Erdos-Renyi network
    * fast for non-sparse networks
    * the sparce version should be implemented
    """
    net=pynet.SymmNet()
    for i in range(0,n):
        for j in range(0,i):
            if p>random.uniform(0,1):
                net[i,j]=1
    return net
