import pynet
import netext,percolator,netio
import os
from pylab import *
import copy
import random
import shutil
import Image

### LIST OF CHANGES
#
# JS/280509: Implemented use of labels in visualizeNet: if dict labels
# given, these will be displayed. If uselabels='all', all labels will
# be displayed, no dict needs to be input.  Tested with simple cases
# (uselabels='all', uselabels='none', labels given in dict
# labels. Appears to work.
#
# JS/040609: Added ReturnPlotObject, which generates a matplotlib plot
# object which can be directly displayed e.g. on a canvas

# -----------------------------------------------------------------------------------

# --------------------------------------        

class Myplot(object):
    '''empty container'''
    pass

# ---------------------------------------

def ReturnPlotObject(data,plotcommand='plot',titlestring='',xstring='',ystring=''):

    '''Input: data [[xseries1,yseries1],[xseries2,yseries2],...] (float,int, whatever)
    plotcommand = matplotlib's plot command (default 'plot', could
    also be 'loglog' etc), titlestring=plot title, xstring=x-axis label, ystring=y-axis label.
    Outputs a container object, corresponding to a matplotlib plot. This can be displayed
    in various ways, eg. on a TkInter canvas:
    myplot.canvas=FigureCanvasTkAgg(myplot.thisFigure,master=plotbody)
    myplot.canvas.show()
    plotbody.pack()
    where plotbody is a Frame object.'''

    Nplots=len(data)

    ystrings=ystring.split(':')
    
    if len(ystrings)<Nplots:
        for i in range(0,Nplots-1):
            ystrings.append(ystrings[0])

    titlestrings=titlestring.split(':')
    if len(titlestrings)<Nplots:
        for i in range(0,Nplots-1):
            titlestrings.append(titlestrings[0])

    subplotstring=str(Nplots)+'1'

    myplot=Myplot()
    myplot.thisFigure=Figure(figsize=(5,4),dpi=100)

    myplot.axes=[]
    for i in range(Nplots):
        myplot.axes.append(myplot.thisFigure.add_subplot(subplotstring+str(i+1),title=titlestrings[i],xlabel=xstring,ylabel=ystrings[i]))
        s="myplot.axes[%d].%s(data[%d][0],data[%d][1],'ro-')" % (i,plotcommand,i,i)
        print s
        eval(s)

    myplot.thisFigure.subplots_adjust(hspace=0.5)

    return myplot

# --------------------------------------        

class Myplot(object):
    '''empty container'''
    pass

# ---------------------------------------

def colortuple(value,vmin,vmax):
        '''calculates color tuple (r,g,b) for
           value. Color map goes yellow->blue->red'''

        if not(vmin==vmax):

            vmid=(vmin+vmax)/2.0

            # calculate red component (curve: 255->0->255)

            maxcolor=1.0

            if value<vmid:

                A=-maxcolor/(vmid-vmin)
                B=-A*vmid

            else:

                A=-maxcolor/(vmid-vmax)
                B=-A*vmid

            rc=A*value+B
            if rc<0.0:
                rc=0.0
            elif rc>1.0:
                rc=1.0

            # calculate green component (curve: 255->0)

            A=-maxcolor/(vmax-vmin)
            B=-A*vmax
            gc=A*value+B

            if gc<0.0:
                gc=0.0
            elif gc>1.0:
                gc=1.0

            # calculate blue component (curve: 0->255->0)

            if value<vmid:

                A=-maxcolor/(vmin-vmid)
                B=-A*vmin

            else:   

                A=maxcolor/(vmid-vmax)
                B=-A*vmax

            bc=A*value+B
            if bc<0.0:
                bc=0.0
            elif bc>1.0:
                bc=1.0

        else:

            bc=0.5
            rc=0.5
            gc=0.5

        return tuple([rc,gc,bc])

def plot_edge(plotobject,xcoords,ycoords,width=1.0,colour='k'):

        plotobject.plot(xcoords,ycoords,'-',lw=width,color=colour)

def plot_node(plotobject,x,y,color='w',size=8.0):

        plotobject.plot([x],[y],'yo',markerfacecolor=color,markersize=size)

def VisualizeNet(net,xy,coloredvertices=False,equalsize=False,labels={},showAllNodes=True,vcolor=[1.0,1.0,1.0],vsize=1.0,nodeColors={},bgcolor=[0.0,0.0,0.0],maxwidth=2.0,minwidth=0.2,uselabels='none'):

        '''Visualizes a network. Inputs:
        net  = network to be visualized
        xy = coordinates (usually originating from visuals.Himmeli, e.g. h=visuals.Himmeli(net,...,...) followed by xy=h.getCoordinates()
        coloredvertices = (True/False). If True, i) IF dict nodeColors was given, these colors are used, ii) IF NOT, vcolor is used if given, and if not, nodes are white. If False, node colors are based on strength.
        equalsize = (True/False) True: all vertices are of same size, input as vsize, default 1.0. False: sizes are based on vertex strength.
        showAllNodes = (True/False) something of a quick hack; if True, displays disconnected components and nodes which have no edges left after e.g. thresholding
        bgcolor = [r g b], r/g/b between 0.0 and 1.0. Background color, default is black.
        maxwidth = max width of edges, default 2.0
        minwidth = min width of edges, default 0.2
        uselabels = ('none','all') Determines if node labels are shown. 'none' shows none, 'all' shows all. Note: any labels input in dict labels ({nodename:labelstring}) are always shown;
                    use this dict to show labels next to your chosen nodes of interest'''

        thisfigure=Figure(figsize=(6,6),dpi=100,facecolor=bgcolor)
        axes=thisfigure.add_subplot(111)
        axes.set_axis_bgcolor(bgcolor)

        # sets the color for node labels

        fontcolor='w'
        if bgcolor=='white':
            fontcolor='k'

        # first draw all edges

        edges=list(net.edges)

        wlist=[]
        for edge in edges:
            wlist.append(edge[2])

        wmin=min(wlist)
        wmax=max(wlist)

        if not(wmax==wmin):

            A=(maxwidth-minwidth)/(wmax-wmin)
            B=maxwidth-A*wmax

        else:

            A=1.0
            B=0.0

        for edge in edges:

            width=A*edge[2]+B

            xcoords=[xy[edge[0]][0],xy[edge[1]][0]]

            ycoords=[xy[edge[0]][1],xy[edge[1]][1]]

            colour=colortuple(edge[2],wmin,wmax)

            plot_edge(axes,xcoords,ycoords,width=width,colour=colour)

        # then draw nodes, depending on given options
        # showAllNodes displays also nodes who do not have any edges
        # left after e.g. thresholding

        nodelist=[]
        if showAllNodes:
            for node in xy.keys():
                nodelist.append(node)
        else:
            for node in net:
                nodelist.append(node)

        minnode=2.0
        maxnode=6.0

        strengths=netext.strengths(net)
   
        maxs=max(strengths.values())
        mins=min(strengths.values())

        if not(equalsize):
        
            A=(maxnode-minnode)/(maxs-mins)
            B=maxnode-A*maxs    

        for node in nodelist:

            # first define size

            if equalsize:

                nodesize=vsize
                if (nodesize<1.0):          # hack: Himmeli wants size <1.0
                    nodesize=nodesize*maxnode  # if Himmeli-type size used, scale up

            else:

                if node in net:

                    nodestrength=strengths[node]

                    nodesize=A*strengths[node]+B

                else:

                    nodestrength=mins
                    nodesize=minnode

            # then determine color

            if coloredvertices:

                if len(nodeColors)>0:

                    ctemp=nodeColors[node]

                    if len(ctemp)==6: # recognize as Himmeli-type string ('999999')

                        rc=float(ctemp[0:2])/99.0
                        gc=float(ctemp[2:4])/99.0
                        bc=float(ctemp[4:6])/99.0

                        # this is a stupid hack; sometimes rounding errors result
                        # in rc=1.0 + epsilon and matplotlib complains...

                        if (rc<0.0):
                            rc=0.0
                        elif rc>1.0:
                            rc=1.0

                        if (bc<0.0):
                            bc=0.0
                        elif bc>1.0:
                            bc=1.0

                        if (gc<0.0):
                            gc=0.0
                        elif gc>1.0:
                            gc=1.0

                        color=(rc,gc,bc)

                    else:

                        color=nodeColors[node] #othrwise assume it is a RGB tuple

                else:

                    if len(vcolor)==6:

                        rc=float(vcolor[0:2])/99.0
                        gc=float(vcolor[2:4])/99.0
                        bc=float(vcolor[4:6])/99.0
                        
                        if (rc<0.0):
                            rc=0.0
                        elif rc>1.0:
                            rc=1.0

                        if (bc<0.0):
                            bc=0.0
                        elif bc>1.0:
                            bc=1.0

                        if (gc<0.0):
                            gc=0.0
                        elif gc>1.0:
                            gc=1.0

                        color=(rc,gc,bc)

                    else:

                        color=vcolor         

            else:

                color=colortuple(nodestrength,mins,maxs)
                

            plot_node(axes,x=xy[node][0],y=xy[node][1],color=color,size=nodesize)
            if uselabels=='all':
                axes.annotate(str(node),(xy[node][0],xy[node][1]),color=fontcolor,size=7)
            elif node in labels:
                axes.annotate(labels[node],(xy[node][0],xy[node][1]),color=fontcolor,size=7)

                    

        setp(axes,'xticks','','xticklabels','','yticks','','yticklabels','')

        xylist=xy.values()
        xlist=[]
        ylist=[]
        for elem in xylist:
            xlist.append(elem[0])
            ylist.append(elem[1])

        minx=min(xlist)
        maxx=max(xlist)
        miny=min(ylist)
        maxy=max(ylist)

        xdelta=0.05*(maxx-minx)
        ydelta=0.05*(maxy-miny)

        setp(axes,'xlim',(minx-xdelta,maxx+xdelta),'ylim',(miny-ydelta,maxy+ydelta))


        return thisfigure

            


              
class Himmeli:

    # this class uses the executable Himmeli, which produces an .eps file AND outputs x-y-coordinates of nodes for visualization
    # first we have to find this executable

    if sys.platform=='win32':

        # for Win use direct path (probably works better with the executable network toolbox...)

        himmeliExecutable="himmeli_3.0.1\himmeli.exe"

    else:

        # trick: find out where netext.py is (must be in the netpython directory),
        # then add the rest of the path

        #himmeliExecutable=os.path.dirname(netext.__file__)+"/Himmeli/himmeli.exe"
        himmeliExecutable=os.path.dirname(netext.__file__)+"/../himmeli_3.0.1/himmeli.exe"

        if not(os.path.isfile(himmeliExecutable)):

            # just in case Himmeli was compiled without the .exe...

            #himmeliExecutable=os.path.dirname(netext.__file__)+"/Himmeli/himmeli"
            himmeliExecutable=os.path.dirname(netext.__file__)+"/../himmeli_3.0.1/himmeli"


    # directly complain if Himmeli not found

    if not(os.path.isfile(himmeliExecutable)):

        complaint="Cannot find Himmeli! This is where it should be: "+himmeliExecutable

        raise Exception(complaint)


    epsilon=0.0001 #hack, find the real thing

    def __init__(self,inputnet,time=20,configFile=None,threshold=None,useMST=False,wmin=None,wmax=None,coloredvertices=True,equalsize=True,vcolor="999999",vsize="1.0",coordinates=None,labels={},distanceUnit=1,showAllNodes=True,edgeLabels=False,nodeColors={},treeMode=False,saveFileName=None):
        #Checking that the given net is valid and not empty
        #if net.__class__!=pynet.Net and net.__class__!=pynet.SymmNet:
        if not isinstance(inputnet,pynet.Net):
            raise AttributeError("Unknown net type "+str(inputnet.__class__))
        if len(inputnet._nodes)==0:
            raise AttributeError("The net cannot be empty")

        if wmin==None:
            # finds out smallest and largest weight
            witer=inputnet.weights.__iter__()
            wmin=99999999.0
            wmax=0.0

            for eachitem in witer:
                if eachitem<wmin:
                    wmin=eachitem
                if eachitem>wmax:
                    wmax=eachitem

        if showAllNodes:

            # this is especially designed for thresholded nets, where there may be nodes with zero
            # links in addition to disconnected components. IF coordinates have been calculated
            # for the network WITHOUT THRESHOLDING, augmentNet adds every node mentioned in coordinates
            # to the network (with epsilon-weight "ghost" links). Furthermore, augmentNet joins all
            # disconnected components to the largest component with ghost links. 

            net=self.augmentNet(inputnet,useMST,coordinates,wmin)

        else:

            net=inputnet

        if (showAllNodes or useMST):

            threshold2=[]

            threshold2.append('abs')
            threshold2.append(wmin)
            threshold2.append(wmax)

        #First we need to generate names for this net and its files
        rgen=random.Random()
        netName=str(rgen.randint(1,10000))
        edgFileName="himmeli_tmp"+netName+".edg"
        confFileName="himmeli_tmp"+netName+".cfg"
        vtxFileName="himmeli_tmp"+netName+".vtx"
        coordFileName=netName+".vertices.txt"
        legendFileName=netName+".legend.eps"
        output_confFileName=netName+'.config.txt'
        output_edgFileName=netName+'.edges.txt'
        output_psFileName=netName+'.ps'

        #Then we make config for Himmeli or read it from a file
        if configFile==None:
            config="EdgeHeadVariable\tHEAD\n"
            config+="EdgeTailVariable\tTAIL\n"
            config+="EdgeWeightVariable\tWEIGHT\n"

            config+="FigureLimit\t1\n"
            config+="DecorationMode\ton\n"
            config+="IncrementMode\ton\n"
            if treeMode:
                config+="TreeMode\ton\n"
            else:
                config+="TreeMode\toff\n"
            if coordinates==None:
                config+="TimeLimit\t"+str(time)+"\n"
            else:
                config+="TimeLimit\t0\n"
            if net.isSymmetric():
                config+="ArrowMode\toff\n"
            else:
                config+="ArrowMode\ton\n"
            #config+="PageSize\tauto\tauto\n"
            config+="PageSize\tauto\ta4\n"
            config+="DistanceUnit\t"+str(distanceUnit)+"\n"
            if len(labels)>0 and edgeLabels==False:
                config+="LabelMode\tvertex\n"
            elif len(labels)>0 and edgeLabels==True:
                config+="LabelMode\ton\n"
            else:
                config+="LabelMode\toff\n"
            #config+="PageOrientation\tportrait\n"
            if threshold!=None: #not tested properly           
                filterType=threshold[0]
                minedge=threshold[1]
                maxedge=threshold[2]
                config+="EdgeWeightFilter\t"+filterType+"\t"
                config+=str(0.99*minedge)+"\t"+str(1.01*maxedge)+"\n"
            if (useMST) or (showAllNodes):
                filterType=threshold2[0]
                minedge=threshold2[1]
                maxedge=threshold2[2]
                config+="EdgeWeightMask\t"+filterType+"\t"
                config+=str(0.99*minedge)+"\t"+str(1.01*maxedge)+"\n"



        else:
            configTemplate=open(configFile)
            config=configTemplate.read()
            configTemplate.close()

        #---These are specific for this Himmeli run
        config+="GraphName\t"+netName+"\n"
        config+="EdgeFile\t"+edgFileName+"\n"

        config+="VertexFile\t"+vtxFileName+"\n"
        config+="VertexNameVariable\tVNAME"+"\n"
        config+="VertexLabelVariable\tVLABEL"+"\n"

        if coloredvertices:
            config+="VertexColorVariable\tVCOLOR"+"\n"
        if equalsize:
            config+="VertexSizeVariable\tVSIZE\n"
        if coordinates!=None:
            config+="VertexXVariable\tVX\n"
            config+="VertexYVariable\tVY\n"

            #if showAllNodes:
        #   config+="EdgeWeightMask\tabs\t"+str(2*self.epsilon)+"\t"+str(1/self.epsilon)+"\n"
            #config+="EdgeWeightFilter\tabs\t"+str(2*self.epsilon)+"\t"+str(1/self.epsilon)+"\n"

        #---

        #Now we write all nessesary files for Himmeli to disk
        #Edge file:

        netio.writeNet(net,edgFileName,headers=True)

        #Vertex file:
        self.writeVertexFile(net,vtxFileName,coloredvertices,equalsize,vcolor,vsize,coordinates=coordinates,labels=labels,nodeColors=nodeColors)
        #Config file:
        confFile=open(confFileName,'w')
        confFile.write(config)
        confFile.close()

        #All is set for running Himmeli
        himmeli=os.popen(self.himmeliExecutable+' '+confFileName,'r')
        #print string.join(himmeli.readlines()) #for long debug
        himmeli.close()
        #print himmeli #for short debug

        #Save coordinates produced by Himmeli
        self.coordinates=self._parseCoordinates(coordFileName)

        #Remove files that are not needed anymore
        os.remove(edgFileName)
        os.remove(confFileName)
        os.remove(coordFileName)
        if os.path.isfile(legendFileName):
            os.remove(legendFileName)
        os.remove(output_confFileName)
        os.remove(output_edgFileName)
        os.remove(output_psFileName)
        os.remove(vtxFileName)

        #Finally we save all the information needed later
        self.netName=netName
        self.saveFileName = saveFileName


    def getCoordinates(self):
        return self.coordinates

    def saveEps(self,filename):
        shutil.copyfile(self.netName+"_0001.eps",filename)

    def draw(self):
        im=Image.open(self.netName+"_0001.eps")
        im.show()

    def _parseCoordinates(self,coordFileName):
        coordFile=open(coordFileName)
        coordFile.readline()
        coordinates={}
        for line in coordFile:
            columns=line.split("\t")
            if len(columns)==13:
               #old version:
               #[comp,tail,head,weight,tree,name,x,y,z,degree,treedg,strengt,treestg,dummy]=line.split("\t")
               [comp,name,x,y,z,degree_in,dg_out,strengt_in,strength_out,color,shape,size,label]=line.split("\t")
               if len(name)!=0:
                   try:
                       name=int(name)
                   except ValueError:
                       pass
                   coordinates[name]=(float(x),float(y),float(z))
        return coordinates


        
    def _writeEpsilonEdges(self,net,fileName):

        # obsolete
        # replaced by augmentNet, which generates a new network
        # with the epsilon edges directly added. No need for
        # rewriting to any file; EdgeWeightFilter is always
        # used.

        file=open(fileName,'a')
        last=None
        for node in net:
            if last!=None:
               if net[last,node]==0:
                   file.write(str(node)+"\t"+str(last)+"\t"+str(self.epsilon)+"\n")
            last=node
        file.close()

    def __del__(self):
        if not self.saveFileName:
            if os.path.isfile(self.netName+"_0001.eps"):
                os.remove(self.netName+"_0001.eps")
        else:
            self.saveEps(self.saveFileName)
        
    def augmentNet(self,net,useMST=False, coords=None,wmin=None):
        """Checks if the network is singly connected. If,
        returns the network untouched. If not, connects
        one node of each component to the giant component
        with a very small weight and produces a list of
        these ghost edges. Alternatively, if useMST=true,
        all nodes which are keys in the coordinate list are
        added to the network, joined with epsilon edges.
        This is useful for thresholding
        networks with various thresholds, so that
        even all k=0 nodes are always visible.
        Output augmented net with epsilon edges added"""

        # if min weight not given, find it out

        if wmin==None:
            # finds out smallest weight
            witer=net.weights.__iter__()
            wmin=99999999.0

            for eachitem in witer:
                if eachitem<wmin:
                    wmin=eachitem

        epsilon_factor=25.0

        temp=percolator.getComponents(net)

        sizelist=[]
        for i in temp:
            sizelist.append(len(i))

        mc=max(sizelist)
        maxcomponent_index=0
        for i, v in enumerate(sizelist):
            if v==mc:
                maxcomponent_index=i

        giantmembers=temp[maxcomponent_index]

        Ncomponents=len(temp)
        maxcomponent=len(giantmembers)

        # MAKE A COPY OF THE ORIGINAL NETWORK;
        #
        # deepcopy generated segfaults probably due to C++ interfacing
        # so this is simple and stupid (and slow). 

        N=len(net._nodes)

        if (isinstance(net,pynet.SymmFullNet)):
            newnet=pynet.SymmFullNet(N)
        else:
            newnet=pynet.SymmNet()
    
        edges=list(net.edges)

        for edge in edges:

            newnet[edge[0]][edge[1]]=edge[2]

        # newnet=copy.deepcopy(net)

        # if MST not used, just connect all disjoint
        # components

        if useMST==False:

            if Ncomponents!=1:

                # find out which component is the giant one
                # list its members for ghost edge targets


                gianttemp=copy.deepcopy(giantmembers)
                giantmembers=[]
                for i in range(0,len(gianttemp)):
                    giantmembers.append(gianttemp.pop())

                for index,c in enumerate(temp):

                    if index!=maxcomponent_index:

                        ghostsource=c.pop()
                        tindex=int(math.ceil(random.random()*float(len(giantmembers)-1)))
                        ghosttarget=giantmembers[tindex]

                        newnet[ghostsource][ghosttarget]=wmin/epsilon_factor

        # next, if useMST=True, use keys of coordinates to insert all
        # original vertices to the net, again with epsilon weights

        else:

            last=None

            for newnode in coords.keys():

                if last!=None:
                   if newnet[last][newnode]==0:
                          newnet[newnode][last]=wmin/epsilon_factor   # JS 290509 changes [newnode,last] to [newnode][last]

                last=newnode

        return newnet


    def writeVertexFile(self,net,filename,coloredvertices=True,equalsize=True,singlecolor="999999",vcolors=0,singlesize="0.3",vsizes=0,coordinates=None,labels={},nodeColors={}):
        file=open(filename,'w')

        if len(nodeColors)>0:
            coloredvertices=True

        file.write("VNAME")
        file.write("\tVLABEL")
        if coloredvertices:
            file.write("\tVCOLOR")
        if equalsize:
            file.write("\tVSIZE")
        if coordinates!=None:
            file.write("\tVX")
            file.write("\tVY")
        file.write("\n")
        for i in net:
            file.write(str(i))
            try:
                file.write("\t"+str(labels[i]))
            except KeyError:
                file.write("\t"+str(i))
            if coloredvertices:
                if len(nodeColors)>0:
                    file.write("\t"+str(nodeColors[i]))
                else:
                    file.write("\t"+singlecolor)
            if equalsize:
                file.write("\t"+singlesize)
            if coordinates!=None:
                file.write("\t"+str(coordinates[i][0]))
                file.write("\t"+str(coordinates[i][1]))
            file.write("\n")


    
def drawNet(net,labels={},coordinates=None,showAllNodes=False):
    """Display a picture of the network using Himmeli
    """
    h=Himmeli(net,labels=labels,coordinates=coordinates,showAllNodes=showAllNodes)
    h.draw()
        



