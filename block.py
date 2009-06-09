import numpy
from numpy import array

class rimatrix(numpy.array):
    def __init__(self,args):
        super(array,self)
        self.reindexing=array(range(0,len(self)))

    def getReindexing(self):
        return self.reindexing;

    def __getitem__(self,args):
        if isinstance(args,tuple):
            return array.__getitem__(self,(reindexing(args[0]),reindexing(args[1])))
        else:
            return array.__getitem__(self,(reindexing(args),reindexing))

class blockdiag(rimatrix):
    def __init__(self,args):
        super(rimatrix,self)

    def getEnergy(self):
        pass

    
