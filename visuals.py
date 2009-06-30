# -*- coding: latin-1 -*-
import pynet
import netext,percolator,netio,transforms
import os
from pylab import *
import copy
import random
import shutil
import Image


### LIST OF CHANGES
# Riitta 30.6.2009
# In VisualizeNet, changed default to coloredNodes=True, such that giving nodeColors or
# nodeColor as input will be sufficient for nodes to be plotted in
# color.
#
# Riitta 29.6.2009
#
# In VisualizeNet, I changed the option 'coloredvertices' to 'coloredNodes', 'vcolor'
# to 'nodeColor', and 'vsize' to 'nodeSize' to accord with other
# options. I also changed 'vertex' to node in the usage info where
# possible, as it adds unnecessary confusion to a user not familiar
# with networks if both terms are used. 
#
# I also slightly modified the behavior produced by the option coloredNodes,
# because I find it more logical that all white nodes will 
# be produced by the option coloredNodes='False' than with coloredNodes='True'.
# 
# Old usage info:
#        coloredvertices = (True/False). If True, i) IF dict nodeColors
#        was given, these colors are used, ii) IF NOT, vcolor is used
#        if given, and if not, nodes are white. If False, node colors
#        are based on strength.
# Current usage info:
#        coloredNodes = (True/False),
#        nodeColors = dictionary of node colors by node index, and 
#        nodeColor = an RGB color tuple with three values between 0 and 1
#         If coloredNodes='False', nodes are plotted white.
#         If coloredNodes='True', 
#          a) if dictionary 'nodeColors' is given, it is used.
#             If it does not contain a color for every node,
#             the rest are colored with 'nodeColor' if it is given,
#             or white if it is not. 
#          b) if dictionary 'nodeColors' is not given, but 'nodeColor'
#             is given, all nodes are colored with 'nodeColor'.
#          c) if neither dictionary 'nodeColors' nor 'nodeColor' is given,
#             nodes are colored by strength using the colormap 'EdgeColorMap'. 
#              (Please see below for information on 'EdgeColorMap'.)
# 
# I also removed the unused option vsizes=0 from the function writeVertexFile.
#  
# Riitta 29.6.2009
#  - added a function for translating the coordinates of given nodes:
#     shiftCoordinates(xy,nodelist,xshift=0,yshift=0,zshift=0)
#
# Riitta 2506:
#  - added option 'fontsize' to VisualizeNet 
#
# Jari 2406 :
# - updated ReturnPlotObject (used primarily for EDEN toolbox)
# - fixed the node size bug in VisualizeNet
# - added figsize (figsize=(w,h)) as input parameter to VisualizeNet
# - added automatic conversion of edge distances to weights in VisualizeNet & Himmeli (EDEN-specific)
#
# 
# Riitta Toivonen/230609:
# 
# 1) Added the input argument edgeColorMap. Now any pylab colormap can be
# used for setting colors for edges (according to edge weight) and
# nodes (according to node strength).
#
# Jari's default colors (yellow->blue->red) can be used with the
# option edgeColorMap='primary'. Another custom colormap is available
# by the name edgeColorMap='orange'.  All 150 pylab colormaps are
# available (please see help cm, and look for DATA). The 'colortuple'
# function is no longer needed.
#
# 2) I also added the input argument weightLimits.  The tuple
# weightLimits=(minWeight, maxWeight) provides the minimum and maximum
# value for weights. If none are given, (almost) the true min and max
# weights in the network will be used.  If the true min weight is not
# zero, minWeight is set to slightly below true min weight. Otherwise,
# when normalizing the weights, the minimum weights would be
# transformed to zero and the edges not visible at all. The
# weightLimits are used for setting edge colors and width. They enable
# the user to plot several networks (which may have different min and
# max weights) such that a certain color and width always correspond
# to a certain edge weight. Thus, the color and width in the
# visualization can be used to infer edge weight. If the network turns
# out to contain weights above the given maxWeight (below minWeight)
# these will be rounded downwards (upwards) to the given limit. It is
# more reasonable however for the user to provide limits that can
# accommodate all weights, this is just a necessary precaution for the
# case where the given limits are too tight.
# 
# 3) To do the above, I added these methods to VisualizeNet:
#    normalizeWeight(value,weightLimits)
#    setEdgeColorMap(edgeColorMap)
#    setEdgeColor(value,weightLimits,edgeColorMap)
#    setEdgeWidth(value,weightLimits,minwidth,maxwidth)
#
# 4) I also added a few usage examples to the help text
# (visible with help(visuals.VisualizeNet) ).          
#
# 5) I started writing tests for visuals.py. Many more still need to
# be written. They are found in   netpython/tests/visuals/test_visuals.py
#     -Riitta
#
# Jari Saramäki/280509: Implemented use of labels in visualizeNet: if dict labels
# given, these will be displayed. If uselabels='all', all labels will
# be displayed, no dict needs to be input.  Tested with simple cases
# (uselabels='all', uselabels='none', labels given in dict
# labels. Appears to work.
#
# Jari Saramäki/040609: Added ReturnPlotObject, which generates a matplotlib plot
# object which can be directly displayed e.g. on a canvas
# 
# -----------------------------------------------------------------------------------
# 
# --------------------------------------        

class Myplot(object):
    '''empty container'''
    pass

# ---------------------------------------



# --------------------------------------        

class Myplot(object):
    '''empty container'''
    pass

# ---------------------------------------

def ReturnPlotObject(data,plotcommand='plot',titlestring='',xstring='',ystring='',figsize=(5,4),fontsize=14,fontname='Times',addstr='',labelMultiplier=1.2,plotcolor='r',facecolor="#cacfbe",edgecolor=None):

    '''Input: data [[xseries1,yseries1],[xseries2,yseries2],...] (float,int, whatever)
    plotcommand = matplotlib's plot command (default 'plot', could
    also be 'loglog' etc), titlestring=plot title, xstring=x-axis label, ystring=y-axis label.
    Outputs a container object, corresponding to a matplotlib plot. This can be displayed
    in various ways, eg. on a TkInter canvas:
    myplot.canvas=FigureCanvasTkAgg(myplot.thisFigure,master=plotbody)
    myplot.canvas.show()
    plotbody.pack()
    where plotbody is a Frame object.


    quick hack: addstr takes in arguments for plotting command, e.g. ",'ro'","width=0.1", etc. To be fixed.'''

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
    myplot.thisFigure=Figure(figsize=figsize,dpi=100,facecolor=facecolor,edgecolor=edgecolor)

    myplot.axes=[]


    axisfactor=1.0/Nplots
    
    for i in range(Nplots):

        leftcorner=0.2
        width=0.6
        bottom=(0.2+float(i))*axisfactor
        top=0.6*axisfactor

        font={'fontname':'Times','fontsize':fontsize+2}
        
        myplot.axes.append(myplot.thisFigure.add_axes([leftcorner,bottom,width,top],title=titlestrings[i],xlabel=xstring,ylabel=ystrings[i]))
        s="myplot.axes[%d].%s(data[%d][0],data[%d][1]" % (i,plotcommand,i,i)
        s=s+addstr+')'
        eval(s)

        myplot.axes[i].set_title(titlestrings[i],**font)
        
        for tick in myplot.axes[i].get_xticklabels():
            tick.set_fontsize(fontsize)
            tick.set_fontname(fontname)
                                    
        for tick in myplot.axes[i].get_yticklabels():
            tick.set_fontsize(fontsize)
            tick.set_fontname(fontname)

        labels = [myplot.axes[i].get_xaxis().get_label(), myplot.axes[i].get_yaxis().get_label()]
        for label in labels:
            label.set_size( labelMultiplier*fontsize )

        

    myplot.thisFigure.subplots_adjust(hspace=0.5)

    return myplot


def normalizeWeight(value,weightLimits):
    # Transforms a weight to the range (0,1). It is intended that the
    # user should set weightLimits such that the true weights in the
    # network fall between the limits. If this is not the case,
    # weights above given maxweight or below given minweight are
    # truncated. The rest of the values are transformed linearly, such
    # that the range (given minweight, given maxweight) becomes (0,1).
    # 
    #     normalizedWeight= (true weight - given minweight) / (given maxweight - given minweight )
    # 
    if (weightLimits[0]-weightLimits[1])==0: # if given minweight and maxweight are the same, all weights will be equal
        normalizedWeight=1
    elif value<weightLimits[0]: # if weight is smaller than given minweight
        normalizedWeight=0
    elif value>weightLimits[1]: # if weight is larger than given maxweight
        normalizedWeight=1
    else:
        normalizedWeight=(value-weightLimits[0])/float(weightLimits[1]-weightLimits[0])
    return normalizedWeight 


def setEdgeColorMap(edgeColorMap):
    # Sets a colormap for edges. Two options of our own are available
    # ('orange' and 'primary'), in addition to the 150 pylab readymade
    # colormaps. 
    
    if edgeColorMap=='primary':
        # Jari's map: yellow->blue->red 
        myMap=get_cmap()
        myMap._segmentdata={
            'red': ( (0,1,1), (0.5,0,0), (1,1,1)  ),
            'green': ( (0,1,1), (0.5,0.5,0.5), (1,0,0) ),
            'blue': ( (0,0,0), (0.5,1,1), (1,0,0) ),
            }

    elif edgeColorMap=='orange':
        # Riitta's color map from white through yellow and orange to red 
        myMap=get_cmap()
        myMap._segmentdata = { 'red'  : ( (0.,.99,.99), (0.2,.98,.98), (0.4,.99,.99), (0.6,.99,.99), (0.8,.99,.99), (1.0,.92,.92) ),
                               'green': ( (0,0.99,0.99), (0.2,.89,.89),  (0.4,.80,.80), (0.6,.50,.50), (0.8,.33,.33), (1.0,.10,.10) ),
                               'blue' : ( (0,.99,.99), (0.2,.59,.59), (0.4,.20,.20), (0.6,0.0,0.0), (0.8,0.0,0.0), (1.0,.03,.03) )  }

    else:
        try:
            myMap=get_cmap(edgeColorMap)
        except AssertionError:
            comment='\nCould not recognize given edgeColorMap name \''+ edgeColorMap+'\' \n\n'
            raise AssertionError(comment)            
    return myMap


# ---------------------------------------

def setEdgeColor(value,weightLimits,edgeColorMap):
    # Set edge color by weight (no other option implemented thus far)
    if not (weightLimits[0]-weightLimits[1])==0: 
        normalizedWeight=normalizeWeight(value,weightLimits) 
        color=edgeColorMap(normalizedWeight) 
    else:
        color=(0.5,0.5,0.5)  # gray if all weights are equal
    return color


def setEdgeWidth(value,weightLimits,minwidth,maxwidth):
    # Transforms edge weights to widths in the range  (minwidth,maxwidth).
    # If given minwidth and maxwidth are the same, simply use that given width.
    if not(weightLimits[0]-weightLimits[1])==0:
        normalizedWeight=normalizeWeight(value,weightLimits)  # normalizes the weight linearly to the range (0,1)
        width=minwidth+normalizedWeight*(maxwidth-minwidth)   # transforms the normalized weight linearly to the range (minwidth,maxwidth)     
    else:
        width=minwidth # if given minwidth and maxwidth are the same, simply use that width
    return width
    

def plot_edge(plotobject,xcoords,ycoords,width=1.0,colour='k'):
    
    plotobject.plot(xcoords,ycoords,'-',lw=width,color=colour)

def plot_node(plotobject,x,y,color='w',size=8.0):
    
    plotobject.plot([x],[y],'yo',markerfacecolor=color,markersize=size)


# ---------------------------------------

def VisualizeNet(net,xy,figsize=(6,6),coloredNodes=True,equalsize=False,labels={},fontsize=7,showAllNodes=True,nodeColor='None',nodeSize=1.0,nodeColors={},bgcolor='white',maxwidth=2.0,minwidth=0.2,uselabels='none',edgeColorMap='winter',weightLimits='none'): 

        '''
        Visualizes a network. Inputs:

        net = network to be visualized (of type SymmNet() ).

        xy = coordinates (usually originating from visuals.Himmeli,
        e.g. h=visuals.Himmeli(net,...,...) followed by
        xy=h.getCoordinates()

        figsize=(x,y) (default (6,6)) Size of the figure produced by VisualizeNet


        coloredNodes = (True/False),
        nodeColors = dictionary of node colors by node index, and 
        nodeColor = an RGB color tuple with three values between 0 and 1
         If coloredNodes='False', nodes are plotted white.
         If coloredNodes='True', 
          a) if dictionary 'nodeColors' is given, it is used.
             If it does not contain a color for every node,
             the rest are colored with 'nodeColor' if it is given,
             or white if it is not. 
          b) if dictionary 'nodeColors' is not given, but 'nodeColor'
             is given, all nodes are colored with 'nodeColor'.
          c) if neither dictionary 'nodeColors' nor 'nodeColor' is given,
              nodes are colored by strength using the colormap 'EdgeColorMap'. 
              (Please see below for information on 'EdgeColorMap'.)

        equalsize = (True/False) True: all nodes are of same size,
        input as nodeSize, default 1.0. False: sizes are based on node
        strength.

        showAllNodes = (True/False) something of a quick hack; if
        True, displays disconnected components and nodes which have no
        edges left after e.g. thresholding

        bgcolor = [r g b], r/g/b between 0.0 and 1.0. Background
        color, default is black.

        maxwidth = max width of edges as plotted, default 2.0

        minwidth = min width of edges as plotted, default 0.2

        uselabels = ('none','all') Determines if node labels are shown.
        'none' shows none, 'all' shows all. Note: any labels input in
        dict labels ({nodename:labelstring}) are always shown; use
        this dict to show labels next to your chosen nodes of
        interest. 
        
        fontsize=size  Sets font size for labels. Default is 7. 

        edgeColorMap=myMap allows the user to set color scheme for
        edges.  Edges are always colored according to edge weights,
        which are first normalized to the range (0,1) and then
        transformed to colors using edgeColorMap. There are 150
        colormaps available in pylab; for a full listing, please see
        help(pylab.cm) (and look for DATA). Or try, for example,
        edgeColorMap='orange' or edgeColorMap='primary', two colormaps
        of our own that are not available in pylab.

        weightLimits=(0,5) The tuple (minWeight, maxWeight) provides
        the minimum and maximum value for weights. If none are given,
        (nearly) the true min and max weights in the network will be
        used. The weightLimits are used for setting edge colors and
        width. They enable the user to plot several networks (which
        may have different min and max weights) such that a certain
        color and width always correspond to a certain edge
        weight. Thus, the color and width in the visualization can be
        used to infer edge weight. If the network turns out to contain
        weights above the given maxWeight (below minWeight) these will
        be rounded downwards (upwards) to the given limit. It is more
        reasonable however for the user to provide limits that can
        accommodate all weights, this is just a necessary precaution
        for the case where the given limits are too tight.


        Usage examples:
            m=pynet.SymmNet()
            m[0][1]=1.0
            m[1][2]=3.5
            m[0][2]=5.0

            Here are the coordinates, a dictionary that contains 2-tuples 
            xy={}
            xy[0]=(0,0)
            xy[1]=(4,0)
            xy[2]=(2,3) 

            f=FigureCanvasBase(visuals.VisualizeNet(m,xy))
            f.print_eps("tmp.eps",dpi=80.0)

            f=FigureCanvasBase(visuals.VisualizeNet(m,xy,edgeColorMap='orange'))
            f.print_eps("tmp2.eps",dpi=80.0)

            f=FigureCanvasBase(visuals.VisualizeNet(m,xy,edgeColorMap='orange',equalsize=True,nodeSize=16))
            f.print_eps("tmp3.eps",dpi=80.0)

            (General questions: Is there a neater way to output the
            figures than using FigureCanvasBase? How can I have a look
            at the figures from within python, without saving them to
            .eps files?)
            
        '''

        # the following is for the EDEN software, where "nets" or nets
        # derived from matrices can have edge distances instead of weights 

        if hasattr(net,'matrixtype'):

            if net.matrixtype==0:

                net=transforms.dist_to_weights(net)
        
        thisfigure=Figure(figsize=figsize,dpi=100,facecolor=bgcolor)
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

        # If weightLimits were not given, use (almost) the true min
        # and max weights in the network. Note: using a value slightly
        # below wmin, because otherwise when normalizing the weights,
        # the minimum weights would be transformed to zero and the
        # edges not visible at all.  - Riitta
        
        if weightLimits=='none':
            if wmin==0:
                weightLimits=(wmin,wmax)
            else:
                weightLimits=(wmin-0.00001,wmax) 
        
        myEdgeColorMap=setEdgeColorMap(edgeColorMap)
        
        for edge in edges:

            width=setEdgeWidth(edge[2],weightLimits,minwidth,maxwidth)

            colour=setEdgeColor(edge[2],weightLimits,myEdgeColorMap)

            xcoords=[xy[edge[0]][0],xy[edge[1]][0]]

            ycoords=[xy[edge[0]][1],xy[edge[1]][1]]

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

                nodesize=nodeSize
                if (nodesize<1.0):          # hack: Himmeli wants size <1.0
                    nodesize=nodesize*maxnode  # if Himmeli-type size used, scale up

            else:

                if node in net:

                    nodesize=A*strengths[node]+B

                else:

                    nodesize=minnode

            if node in net:
                nodestrength=strengths[node]
            else:
                nodestrength=mins     # this is for nodes which appear in MST coords (i.e. have zero links)
                                      # and are thus not included in net, but should yet be displayed when
                                      # visualizing a thresholded network

            # then determine color

            if coloredNodes:

                if len(nodeColors)>0: # if dict nodeColors is given

                    if not nodeColors.get(node): # if node is not contained in dict nodeColors 
                        if not nodeColor=='None':
                            color=nodeColor # use nodeColor if given
                        else:
                            color=(1,1,1) # white if not
                    else:  # if node IS contained in dict nodeColors, use nodeColors[node]   
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
                            color=nodeColors[node] #otherwise assume it is an RGB tuple

                elif not nodeColor=='None': # if dict nodeColors is not given but nodeColor is
                    if len(nodeColor)==6:

                        rc=float(nodeColor[0:2])/99.0
                        gc=float(nodeColor[2:4])/99.0
                        bc=float(nodeColor[4:6])/99.0
                        
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

                        color=nodeColor         

                else:
                    
                    color=setEdgeColor(nodestrength,(mins,maxs),myEdgeColorMap) # use the same colormap for nodes as for edges (now the name edgeColorMap is a bit misleading... Could change it to just colorMap, or alternatively add another input option, 'nodeColorMap') 
                     #color=colortuple(nodestrength,mins,maxs)
            else:
                color=(1.0,1.0,1.0)  # if coloredNodes=True, use white 
                     

            plot_node(axes,x=xy[node][0],y=xy[node][1],color=color,size=nodesize)
            if uselabels=='all':
                axes.annotate(str(node),(xy[node][0],xy[node][1]),color=fontcolor,size=fontsize)
            elif node in labels:
                axes.annotate(labels[node],(xy[node][0],xy[node][1]),color=fontcolor,size=fontsize)

                    

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


            
# ---------------------------------------
              
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

    def __init__(self,inputnet,time=20,configFile=None,threshold=None,useMST=False,wmin=None,wmax=None,coloredNodes=True,equalsize=True,nodeColor="999999",nodeSize="1.0",coordinates=None,labels={},distanceUnit=1,showAllNodes=True,edgeLabels=False,nodeColors={},treeMode=False,saveFileName=None):
        #Checking that the given net is valid and not empty
        #if net.__class__!=pynet.Net and net.__class__!=pynet.SymmNet:
        if not isinstance(inputnet,pynet.Net):
            raise AttributeError("Unknown net type "+str(inputnet.__class__))
        if len(inputnet._nodes)==0:
            raise AttributeError("The net cannot be empty")

        # another EDEN-specific piece of code: if the network is a distance matrix/network,
        # first transform distances to weights

        if hasattr(inputnet,'matrixtype'):

            if inputnet.matrixtype==0:

                inputnet=dist_to_weights(inputnet)

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

        if coloredNodes:
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
        self.writeVertexFile(net,vtxFileName,coloredNodes,equalsize,nodeColor,nodeSize,coordinates=coordinates,labels=labels,nodeColors=nodeColors)
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
        # original nodes to the net, again with epsilon weights

        else:

            last=None

            for newnode in coords.keys():

                if last!=None:
                   if newnet[last][newnode]==0:
                          newnet[newnode][last]=wmin/epsilon_factor   # JS 290509 changes [newnode,last] to [newnode][last]

                last=newnode

        return newnet


    def writeVertexFile(self,net,filename,coloredNodes=True,equalsize=True,singlecolor="999999",vcolors=0,singlesize="0.3",coordinates=None,labels={},nodeColors={}):
        file=open(filename,'w')

        if len(nodeColors)>0:
            coloredNodes=True

        file.write("VNAME")
        file.write("\tVLABEL")
        if coloredNodes:
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
            if coloredNodes:
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

            
# ---------------------------------------
    
def drawNet(net,labels={},coordinates=None,showAllNodes=False):
    """Display a picture of the network using Himmeli
    """
    h=Himmeli(net,labels=labels,coordinates=coordinates,showAllNodes=showAllNodes)
    h.draw()


# ---------------------------------------        

# def shiftCoordinates(xy,nodelist,shift):
def shiftCoordinates(xy,nodelist,xshift=0,yshift=0,zshift=0):
    """ Translates coordinates of given nodes. 
    
        Takes in:
        
               xy, a dictionary in which item 'node' is a tuple
               containing the coordinates of 'node'. They must contain
               either two or three elements, as in (xcoord,ycoord) or
               (xcoord,ycoord,zcoord).

               nodelist, listing the subset of keys in xy that need to be translated

               xshift, yshift, zshift, whose values indicate how much
               to shift the coordinates. Each defaults to zero. If the
               coordinate list contains tuples of length two, zshift
               will be ignored.

        Works for tuples containing two or three coordinates.
        Returns the modified coordinates. """
    
    for node in nodelist:
        coords=xy[node]
        if len(coords)==2:
            xy[node]=(coords[0]+xshift,coords[1]+yshift)
        elif len(coords)==3:
            xy[node]=(coords[0]+xshift,coords[1]+yshift,coords[2]+zshift)
        else:
            raise ValueError('\nThe coordinate tuples should contain two or three elements.\n') 
        

    return xy

# ---------------------------------------  


if __name__ == '__main__':
    """Run unit tests if called."""
    from tests.test_visuals import *
    unittest.main()
