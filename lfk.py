import pynet,communities
from numpy.core.fromnumeric import argmax

def getNodeFitnessForAll(net,com,alpha,useStrength=True):    
    inK=[]
    allK=[]
    comset=set(com)
    for node in com:
        allK.append(net[node].strength())
        neighbors=set(net[node])
        temp_inK=0.0
        for neighbor in net[node]:
            if neighbor in comset:
                temp_inK+=net[node,neighbor]
        inK.append(temp_inK)
    suminK=float(sum(inK))
    sumallK=float(sum(allK))
    fitness=[]
    constFitness=suminK/pow(sumallK,alpha)
    for i in range(0,len(inK)):
        fitness.append(constFitness-float(suminK-2*inK[i])/float(pow(sumallK-allK[i],alpha)))
    return fitness
    

def getNodeFitness(net,com,anode,alpha,useStrength=True):
    compa=list(set(com).union(set([anode])))
    comma=list(set(com)-set([anode]))
    return getFitness(net,compa,alpha,useStrength)-getFitness(net,comma,alpha,useStrength)

def getFitness(net,com,alpha,useStrength=True):
    if useStrength:
        allK=sum(map(lambda x:net[x].strength(),com))
        inK=0
        for node in com:
            for neigh in net[node]:
                if neigh in com:
                    inK+=net[node,neigh]
    else:
        allK=sum(map(lambda x:net[x].deg(),com))
        inK=0
        for node in com:
            for neigh in net[node]:
                if neigh in com:
                    inK+=1
    return float(inK)/pow(float(allK),alpha)

def getNeighborNodes(net,com):
    neighbors=set()
    for node in com:
        for neighbor in net[node]:
            if neighbor not in com:
                neighbors.add(neighbor)
    return list(neighbors)

def detectCommunityForNode(net,alpha,node,useStrength=True):
    com=[node]
    cont=True
    while cont==True and len(com)>0:
        neighbors=getNeighborNodes(net,com)
        if len(neighbors)==0:
            break
        fitness=map(lambda x:getNodeFitness(net,com,x,alpha,useStrength),neighbors)
        best=argmax(fitness)
        if fitness[best]<0:
            cont=False
        else:
            com.append(neighbors[best])
            remove=True
            while remove==True:
                remove=False
                newcom=[]
                fitness=getNodeFitnessForAll(net,com,alpha,useStrength)
                for i,n in enumerate(com):
                    #if getNodeFitness(net,com,n,alpha,useStrength)>=0:
                    if fitness[i]>=0:
                        newcom.append(n)
                    else:
                        remove=True
                com=newcom
    return com

def detectCommunities(net,alpha,useStrength=True):
    todo=set(list(net))
    cmap={}
    while len(todo)>0:
        node=todo.pop()
        print "Nodes left: "+str(len(todo))+" now processing node: "+ str(node)
        com=detectCommunityForNode(net,alpha,node,useStrength)
        todo=todo-set(com)
        cmap[node]=com
    return communities.NodeFamily(cmap)
