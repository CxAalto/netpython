from __future__ import with_statement

# -*- coding: latin-1 -*-
import pynet
import netext,percolator,netio,transforms
import os
from pylab import *
import numpy as np
import copy
import random
import shutil
import Image



# --------------------------------------        

class Myplot(object):
    '''empty container'''
    pass

# ---------------------------------------

def ReturnColorMapPlot(colormap,figsize=(2,0.15)):

    thisfigure=Figure(figsize=figsize,dpi=100)
    axes=thisfigure.add_subplot(1,1,1)
    #myplot.axes.append(myplot.thisFigure.add_axes([0.0,0.0,3.0,1.0]))
    axes.set_axis_off()


    a=np.outer(ones(10),arange(0,1,0.01),)

    axes.imshow(a,aspect='auto',cmap=setColorMap(colormap),origin="lower")

    return thisfigure
    

# ---------------------------------------

def ReturnPlotObject(data,plotcommand='plot',titlestring='',xstring='',
                     ystring='',figsize=(5,4),fontsize=14,fontname='Times',
                     addstr='',labelMultiplier=1.2,plotcolor='r',
                     facecolor="#cacfbe",edgecolor=None):
    """Input: data [[xseries1,yseries1],[xseries2,yseries2],...]
    (float,int, whatever)

    plotcommand = matplotlib's plot command (default 'plot', could
    also be 'loglog' etc), titlestring=plot title, xstring=x-axis
    label, ystring=y-axis label.

    Outputs a container object, corresponding to a matplotlib
    plot. This can be displayed in various ways, eg. on a TkInter
    canvas:
    myplot.canvas=FigureCanvasTkAgg(myplot.thisFigure,master=plotbody)
    myplot.canvas.show() plotbody.pack() where plotbody is a Frame
    object.


    quick hack: addstr takes in arguments for plotting command,
    e.g. ",'ro'","width=0.1", etc. To be fixed.
    """
    Nplots = len(data)

    ystrings=ystring.split(':')
    
    if len(ystrings) < Nplots:
        for i in range(0, Nplots-1):
            ystrings.append(ystrings[0])

    titlestrings = titlestring.split(':')
    if len(titlestrings) < Nplots:
        for i in range(0, Nplots-1):
            titlestrings.append(titlestrings[0])

    subplotstring = str(Nplots)+'1'

    myplot = Myplot()
    myplot.thisFigure = Figure(figsize=figsize,dpi=100,facecolor=facecolor,
                               edgecolor=edgecolor)
    myplot.axes=[]

    axisfactor=1.0/Nplots
    
    for i in range(Nplots):
        leftcorner=0.2
        width=0.6
        bottom=(0.2+float(i))*axisfactor
        top=0.6*axisfactor

        font={'fontname':'Times','fontsize':fontsize+2}
        
        myplot.axes.append(myplot.thisFigure.add_axes([leftcorner,bottom,
                                                       width,top],
                                                      title=titlestrings[i],
                                                      xlabel=xstring,
                                                      ylabel=ystrings[i]))
        s = "myplot.axes[%d].%s(data[%d][0],data[%d][1]" % (i,plotcommand,i,i)
        s += addstr + ')'
        eval(s)

        myplot.axes[i].set_title(titlestrings[i],**font)
        
        for tick in myplot.axes[i].get_xticklabels():
            tick.set_fontsize(fontsize)
            tick.set_fontname(fontname)
                                    
        for tick in myplot.axes[i].get_yticklabels():
            tick.set_fontsize(fontsize)
            tick.set_fontname(fontname)

        labels = [myplot.axes[i].get_xaxis().get_label(),
                  myplot.axes[i].get_yaxis().get_label()]
        [lb.set_size(labelMultiplier*fontsize) for lb in labels]

    myplot.thisFigure.subplots_adjust(hspace=0.5)

    return myplot

def normalizeValue(value,valueLimits):
    """Transforms a numerical value to the range (0,1).

    It is intended that the user should set valueLimits such that the
    true values fall between the limits. If this is not the case,
    values above given maxval or below given minval are truncated. The
    rest of the values are transformed linearly, such that the range
    (given minval, given maxval) becomes (0,1).
     
    normalizedValue= (true_val-given minval)/(given_maxval-given_minval)
    """ 
    if (valueLimits[0]-valueLimits[1]) == 0: 
        # If given minval and maxval are the same, all values will be
        # equal.
        normalizedValue=1
    elif value < valueLimits[0]:
        # If value is smaller than given minval
        normalizedValue=0
    elif value>valueLimits[1]:
        # If value is larger than given maxval
        normalizedValue=1
    else:
        normalizedValue=(value-valueLimits[0])/float(valueLimits[1] -
                                                     valueLimits[0])
    return normalizedValue 


def setColorMap(colorMap):
    """Set a colormap for edges.

    Two options of our own ('orange' and 'primary') are available in
    addition to the 150 pylab readymade colormaps (which can be listed
    with help matplotlib.cm ).

    Usage:
        myMap = setColorMap('bone')
    """
    if hasattr(colorMap, '_segmentdata'):
        return colorMap

    known_colormaps = ('primary', 'orange', 'bluered')
    if colorMap in known_colormaps:
        if colorMap == 'primary':
            # Jari's map: yellow->blue->red 
            segmentdata={'red': ( (0,1,1),(0.5,0,0), (1,1,1)  ),
                         'green': ( (0,1,1), (0.5,0.5,0.5), (1,0,0) ),
                         'blue': ( (0,0,0), (0.5,1,1), (1,0,0) )}
        elif colorMap=='orange':
            # Riitta's color map from white through yellow and orange to red 
            segmentdata = { 'red'  : ( (0.,.99,.99), 
                                       (0.2,.98,.98), 
                                       (0.4,.99,.99), 
                                       (0.6,.99,.99), 
                                       (0.8,.99,.99), 
                                       (1.0,.92,.92) ),
                            'green': ( (0,0.99,0.99), 
                                       (0.2,.89,.89),  
                                       (0.4,.80,.80), 
                                       (0.6,.50,.50), 
                                       (0.8,.33,.33), 
                                       (1.0,.10,.10) ),
                            'blue' : ( (0,.99,.99), 
                                       (0.2,.59,.59), 
                                       (0.4,.20,.20), 
                                       (0.6,0.0,0.0), 
                                       (0.8,0.0,0.0), 
                                       (1.0,.03,.03) )  }
        elif colorMap=='bluered':
            segmentdata={'red':  ( (0,0,0), 
                                   (0.17,0.25,0.25), 
                                   (0.33,0.7,0.7), 
                                   (0.5,.87,.87), 
                                   (0.67,.97,.97),  
                                   (0.83,.93,.93), 
                                   (1,.85,.85) ),
                         'green': ( (0,0,0), 
                                    (0.1667,0.53,0.53), 
                                    (0.3333,.8,.8), 
                                    (0.5,.9,.9), 
                                    (0.6667,.7,.7),
                                    (0.8333,.32,.32), 
                                    (1,.07,.07) ),
                         'blue': ( (0,.6,.6),  
                                   (0.1667,.8,.8),    
                                   (0.3333,1,1),    
                                   (0.5,.8,.8),    
                                   (0.6667,.33,.33),    
                                   (0.8333,.12,.12),
                                   (1,.05,.05) ) }
        myMap = matplotlib.colors.LinearSegmentedColormap(colorMap, segmentdata)
    else:
        try:
            myMap=get_cmap(colorMap)
        except AssertionError:
            comment = "Could not recognize given colorMap name '%s'" % colorMap
            raise AssertionError(comment)
    return myMap


def getConstantColorMap(rgb=(0,0,0)):
    """Return a colormap with constant color.

    Parameters
    ----------
    rgb : tuple (r, g, b)
        The color as RGB tuple. Each value must be between 0 and 1.

    Return
    ------
    cm : colorMap
        The colormap that has just one constant color.
    """
    cm={
        'red':  ( (0,rgb[0],rgb[0]), 
                  (1,rgb[0],rgb[0]) ),
        'green': ( (0,rgb[1],rgb[1]), 
                   (1,rgb[1],rgb[1]) ),
        'blue': ( (0,rgb[2],rgb[2]), 
                  (1,rgb[2],rgb[2]) ) }

    return matplotlib.colors.LinearSegmentedColormap("constant colormap",cm)  


# ---------------------------------------

def getNodeColors(net,colorwith="strength",useColorMap="orange",parentnet=[]):
    """Returns a dictionary {node:color}. The colors are set based
    on either node strengh (colorwith="strength", default) 
    or any nodeProperty. For cases where e.g. nodes which have been thresholded
    out (k=0), the input parameter parentnet can be used - parentnet should contain the original
    network *before* thresholding, i.e. containing all original nodes and
    their attributes. IF parentnet is given, i) if strength is used, its nodes
    which are NOT in net colored gray, ii) if properties
    are used, its nodes are colored similarly to those nodes in net. Also the
    dictionary which is returned contains then all nodes in parentnet"""

    myNodeColors=setColorMap(useColorMap)

    nodeColors={}

    if colorwith=="strength":

        if hasattr(net,'matrixtype'):
            if net.matrixtype==0:        
                net=transforms.dist_to_weights(net)

        strengths = netext.strengths(net)
        max_value = max(strengths.values())
        min_value = min(strengths.values())

        if len(parentnet)>0:        # if we want the dict to include nodes not in net
            for node in parentnet:
                if node in net:     # if the node is in net, use its strength for color
                    nodeColors[node]=setColor(strengths[node],(min_value,max_value),myNodeColors)
                else:               # otherwise color it gray
                    nodeColors[node]=(0.5,0.5,0.5)
        else:
            for node in net:        # if parentnet not given, just color nodes by strength
                nodeColors[node]=setColor(strengths[node],(min_value,max_value),myNodeColors)
    else:

        numeric_props=netext.getNumericProperties(net)
        # first check if colorwith is a numeric property
        if colorwith in numeric_props:
            values=[]
            if len(parentnet)>0:    # again if we want to include nodes not in net
                for node in parentnet:  # first get min and max value of property
                    values.append(parentnet.nodeProperty[colorwith][node])

                min_value=min(values)
                max_value=max(values)
                for node in parentnet: # then set colors according to property
                    nodeColors[node]=setColor(parentnet.nodeProperty[colorwith][node],(min_value,max_value),myNodeColors)
            else:                   # otherwise do the above for nodes in net
                for node in net:
                    values.append(net.nodeProperty[colorwith][node])
                
                min_value=min(values)
                max_value=max(values)

                for node in net:
                    nodeColors[node]=setColor(net.nodeProperty[colorwith][node],(min_value,max_value),myNodeColors)
        
        else:
            # colorwith is not a numeric property, so look up unique values
            # and give them integer numbers

            values={} # empty dict for values
           
            if len(parentnet)>0:# if there are nodes not in net
                props=list(set(parentnet.nodeProperty[colorwith].values()))
            else:
                props=list(set(net.nodeProperty[colorwith].values()))

            for i,prop in enumerate(props):
                values[prop]=i+1

            # now all property strings have a numerical value

            min_value=1
            max_value=max(values.values())

            if len(parentnet)>0:

                for node in parentnet:
                    nodeColors[node]=setColor(values[parentnet.nodeProperty[colorwith][node]],(min_value,max_value),myNodeColors)
                else:
                    for node in net:
                        nodeColors[node]=setColor(values[net.nodeProperty[colorwith][node]],(min_value,max_value),myNodeColors)



    if len(nodeColors)==0:  # finally if for whatever reason no nodes were colored, just set them gray
        if len(parentnet)>0:
            for node in parentnet:
                nodeColors[node]=(0.5,0.5,0.5)
        else:
            for node in net:
                nodeColors[node]=(0.5, 0.5, 0.5)

    return nodeColors

# ------------------------------------------

def getNodeSizes(net,size_by="strength",minsize=2.0,maxsize=6.0):
    """Returns a dictionary {node:size} for visualizations. The sizes
    are set using either node strength"""

    nodeSizes={}

    if size_by=="strength":

        if hasattr(net,'matrixtype'):
            if net.matrixtype==0:        
                net=transforms.dist_to_weights(net)

        strengths = netext.strengths(net)
        maxs = max(strengths.values())
        mins = min(strengths.values())           

        if maxs==mins:
            A=0
        else:
            A=(maxsize-minsize)/(maxs-mins)
        B=maxsize-A*maxs

        for node in net:
            nodeSizes[node]=A*strengths[node]+B

    elif size_by=="fixed":
        for node in net:
            nodeSizes[node]=maxsize
    else:
        numeric_props=netext.getNumericProperties(net)
        if size_by in numeric_props:
            values=[]
            for node in net:
                values.append(net.nodeProperty[size_by][node])

            minval=min(values)
            maxval=max(values)

            if maxval==minval:
                A=0
            else:
                A=(maxsize-minsize)/(maxval-minval)

            B=maxsize-A*maxval
            for node in net:
                nodeSizes[node]=A*net.nodeProperty[size_by][node]+B

    return nodeSizes
          

def setColor(value,valueLimits,colorMap):
    """Converts a numerical value to a color.

    The value is scaled linearly to the range (0...1) using the
    function normalizeValue and the limits valueLimits. This scaled
    value is used to pick a color from the given colormap. The
    colormap should take in values in the range (0...1) and produce a
    three-tuple containing an RGB color, as in (r,g,b).
    """
    if valueLimits[0] < valueLimits[1]: 
        normalizedValue = normalizeValue(value,valueLimits) 
        color = colorMap(normalizedValue) 
    else:
        color=(0.5,0.5,0.5)  # gray if all values are equal
    return color


def setEdgeWidth(value,weightLimits,minwidth,maxwidth):
    """Transforms edge weights to widths in the range (minwidth,
    maxwidth). If given minwidth and maxwidth are the same, simply use
    that given width.
    """
    if not(weightLimits[0]-weightLimits[1])==0:
        # Normalizes the weight linearly to the range (0,1)
        normalizedWeight=normalizeValue(value,weightLimits)  
        # Transforms the normalized weight linearly to the range
        # (minwidth,maxwidth)
        width=minwidth+normalizedWeight*(maxwidth-minwidth)   
    else:
        # If given minwidth and maxwidth are the same, simply use that width.
        width=minwidth 
    return width

   
def plot_edge(plotobject, xcoords, ycoords, width=1.0, colour='k',
              symmetric=True):
    if symmetric:
        plotobject.plot(xcoords,ycoords,'-',lw=width,color=colour)
    else:
        arr = Arrow(xcoords[0], ycoords[0], xcoords[1]-xcoords[0], 
                    ycoords[1]-ycoords[0], edgecolor='none',
                    facecolor=colour,linewidth=width)
        plotobject.add_patch(arr)


def plot_node(plotobject,x,y,color='w',size=8.0,edgecolor='w'):
    plotobject.plot([x], [y], 'yo', markerfacecolor=color,
                    markeredgecolor=edgecolor,markersize=size)


def VisualizeNet(net, xy, figsize=(6,6), coloredNodes=True, equalsize=False,
                 labels=None, fontsize=7, showAllNodes=True, nodeColor=None,
                 nodeEdgeColor='k',
                 nodeSize=1.0, minnode=2.0, maxnode=6.0, nodeColors=None,
                 nodeSizes=None, bgcolor='white', maxwidth=2.0,
                 minwidth=0.2, uselabels='some', edgeColorMap='winter', 
                 weightLimits=None, setNodeColorsByProperty=None,
                 nodeColorMap='winter', nodePropertyLimits=None,
                 nodeLabel_xOffset=None, coloredvertices=None, vcolor=None,
                 vsize=None, frame=False, showTicks=False, axisLimits=None,
                 baseFig=None): 
    """Visualizes a network.

    The coloring of the nodes is decided as follows:
      a) If dictionary `nodeColors` is given, it is used.  If it does
         not contain a color for every node, the rest are colored 
           1) according to property `setNodeColorsByProperty`, if it is
              given, or else
           2) by `nodeColor` if it is given, or
           3) white if neither of the above is given.
      b) If dictionary `nodeColors` is not given, but `nodeColor`
         is given, all nodes are colored with `nodeColor`.
      c) If none of `setNodeColorsByProperty`,`nodeColors` and
         `nodeColor` is given, nodes are colored by strength using the
         colormap `nodeColorMap` (by default 'winter').

    Parameters
    ----------
    net : pynet.SymmNet
        The network to visualize
    xy : dictionary of tuples {node_ID: (x,y,z)}
        Coordinates of all nodes. These usually originate from
        visuals.Himmeli, e.g. 
          h = visuals.Himmeli(net, ...)
          xy = h.getCoordinates()
    figsize : (x,y)
        Size of the output figure in inches. dpi is set to 100.
    coloredNodes : bool
        If True, nodes are colored. Otherwise all nodes are white.
    nodeColors : dict
        Dictionary of node colors by node index.
    nodeSizes : dict
        Dictionary of node sizes by node index.
    minnode : minimum node size, if autoscaling used
    maxnode : maximum node size, if autoscaling used
    nodeColor : RGB color tuple
        Default color of a node. Three values between 0 and 1, for
        example (1.0, 0, 0) is red and (0.5, 0.5, 0.5) is middle gray.
    nodeEdgeColor : any valid matplotlib color (default 'k')
        The color of the edges of nodes. Default is black.
    setNodeColorByProperty : sequence of node indices
        If `setNodeColorsByProperty` is specified, any node not
        appearing in the dictionary `nodeColors` will be colored
        according to the given property (using `nodeColorMap` and
        `nodePropertyLimits`). Option `nodeColors` overrides the
        'setNodeColorsByProperty' option.
    nodeColorMap : str
        A colormap used to color the nodes listed in
        `setNodeColorsByProperty`.
    nodePropertyLimits : [min_val max_val]
        If nodes are coloured according to a nodeProperty, these
        are the min and max values of said property.
    equalsize : bool
        If True, all nodes are of size `nodeSize`. If False, node size
        is based on node strength.
    showAllNodes : bool
        If True, displays disconnected components and nodes which have
        no edges left after e.g. thresholding. (quick hack?)
    bgcolor : sequence (r, g, b)
        Background color as RGB tuple. Default is black.
    minwidth : float
        Minimum width of plotted edges.
    maxwidth : float
        Maximum width of plotted edges.
    labels : dict {nodename:labelstring}
        Dictionary of node labels.
    uselabels : either 'some' (default), 'none' or 'all'
        If 'some', the label is shown for the nodes whose label is
        given in `labels`. If 'all', the node index is shown also for
        those nodes that are not listed in `labels`. If 'none', no
        node labels are printed.
    fontsize : int
        Sets font size for labels.
    edgeColorMap : str or cmap
        Allows the user to set color scheme for edges. Edges are
        always colored according to edge weights, which are first
        normalized to the range (0,1) and then transformed to colors
        using edgeColorMap. There are 150 colormaps available in
        pylab; for a full listing, please see help(pylab.cm) (and look
        for DATA). Or try, for example, edgeColorMap='orange' or
        edgeColorMap='primary', two colormaps of our own that are not
        available in pylab. To make all edges have the same color,
        create a constant color map with getConstantColorMap(rgb).
    weightLimits : tuple (minWeight, maxWeight)
        Provides the minimum and maximum value for weights. If not are
        given, (nearly) the true min and max weights in the network
        will be used. The weightLimits are used for setting edge
        colors and width. They enable the user to plot several
        networks (which may have different min and max weights) so
        that a certain color and width always correspond to a certain
        edge weight. Thus, the color and width in the visualization
        can be used to infer edge weight. If the network turns out to
        contain weights above the given maxWeight (below minWeight)
        these will be rounded downwards (upwards) to the given
        limit.
    nodeLabel_xOffset : float (default nodeSize/40)
        Amount for moving node labels the right so that the text does
        not fall on the nodes.
    frame : bool
        If True, draws a box around the figure.
    showTicks : bool
        If True, adds ticks in the frame. Setting `showTicks` to True
        will always set `frame` to True also.
    axisLimits : tuple ((minX, maxX),(minY, maxY))
        Sets tick limits if `showTicks` is True.
    baseFig : FigureCanvasBase
        If None, the network is drawn on an empty figure, otherwise
        baseFig is used as a starting point.


    Return
    ------
    fig : pylab.Figure
        The plotted network figure.


    Examples
    --------
    >>> from netpython import pynet, visuals
    >>> net = pynet.SymmNet()
    >>> net[0][1] = 1.0
    >>> net[1][2] = 3.5
    >>> net[0][2] = 5.0

    >>> # Here are the coordinates, a dictionary that contains 2-tuples 
    >>> xy = {0:(0,0), 1:(4,0), 2:(2,3)}
    >>> # With larger network use Himmeli to calculate coordinates.
    >>> h = visuals.Himmeli(net)
    >>> xy = h.getCoordinates()

    >>> f = FigureCanvasBase(visuals.VisualizeNet(net,xy))
    >>> f.print_eps("myPlot_1.eps", dpi=80.0)

    >>> f2 = FigureCanvasBase(visuals.VisualizeNet(other_net,xy,baseFig=f))

    >>> f=FigureCanvasBase(visuals.VisualizeNet(net,xy,edgeColorMap='orange'))
    >>> f.print_eps("myPlot_2.eps", dpi=80.0)

    >>> f=FigureCanvasBase(visuals.VisualizeNet(net,xy,edgeColorMap='orange',
                                                equalsize=True, nodeSize=16))
    >>> f.print_eps("myPlot_3.eps", dpi=80.0)

    (General questions: Is there a neater way to output the figures
    than using FigureCanvasBase? How can I have a look at the figures
    from within python, without saving them to .eps files?)
    """

    # Warn about obsolete input arguments
    if coloredvertices!=None or vcolor!=None or vsize!=None:
        warnings.warn("\n\n The options \n"
                      "\t coloredvertices, vcolor, and vsize \n"
                      "are now obsolete. Please use instead \n"
                      "\t coloredNodes, nodeColor, and nodeSize.\n")
    if coloredvertices != None:
        coloredNodes = coloredvertices
    if vcolor != None and nodeColor == None:
        nodeColor = vcolor 
    if vsize != None:
        nodeSize = vsize

    if nodeColors is None:
        nodeColors = {}
    if nodeSizes is None:
        nodeSizes = {}
    if labels is None:
        labels = {}

    # The following is for the EDEN software, where "nets" or nets
    # derived from matrices can have edge distances instead of weights.
    if hasattr(net,'matrixtype'):
        if net.matrixtype==0:        
            net=transforms.dist_to_weights(net)

    if baseFig==None:
        thisfigure=Figure(figsize=figsize,dpi=100,facecolor=bgcolor)
        axes=thisfigure.add_subplot(111)
    else:
        thisfigure=baseFig.figure
        thisfigure.set_facecolor(bgcolor)
        axes=thisfigure.gca()

    axes.set_axis_bgcolor(bgcolor)
    
    if frame == False and showTicks == False: 
        axes.set_axis_off()

    # Set the color for node labels
    fontcolor='w'
    if bgcolor=='white':
        fontcolor='k'
        
    # First draw all edges, if there are any
    edges=list(net.edges)
    if len(edges)>0:
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
        if weightLimits==None:
            if wmin==0:
                weightLimits=(wmin,wmax)
            else:
                weightLimits=(wmin-0.00001,wmax) 

        myEdgeColorMap=setColorMap(edgeColorMap)

        # Plot edges according to weight, beginning with small weight
        sortedEdges=list(net.edges)
        sortedEdges.sort(key=lambda x: x[2])
        for edge in sortedEdges:

            width=setEdgeWidth(edge[2],weightLimits,minwidth,maxwidth)
            colour=setColor(edge[2],weightLimits,myEdgeColorMap)
            xcoords=[xy[edge[0]][0],xy[edge[1]][0]]
            ycoords=[xy[edge[0]][1],xy[edge[1]][1]]
            plot_edge(axes, xcoords, ycoords, width=width, colour=colour,
                      symmetric=net.isSymmetric())


    # Then draw nodes, depending on given options showAllNodes
    # displays also nodes who do not have any edges left after
    # e.g. thresholding
    nodelist=[]
    if showAllNodes:
        nodelist = [node for node in xy.keys()]
    else:
        nodelist = [node for node in net]



    strengths = netext.strengths(net)
    maxs = max(strengths.values())
    mins = min(strengths.values())           

    if not(equalsize):
        A = (0 if maxs == mins else (maxnode-minnode)/(maxs-mins))
        B = maxnode-A*maxs    


    myNodeColorMap=setColorMap(nodeColorMap)

    # If nodes will be colored by setNodeColorsByProperty but
    # nodePropertyLimits were not given, use the true min and max
    # property values in the network.
    if setNodeColorsByProperty != None:
        if nodePropertyLimits == None:
            np=[net.nodeProperty[setNodeColorsByProperty][node] for node in net]
            nodePropertyLimits=(min(np),max(np))

    for node in nodelist:
        # First define size

        if equalsize:
            nodesize=nodeSize
            if (nodesize<1.0):          # hack: Himmeli wants size <1.0
                nodesize=nodesize*maxnode  # if Himmeli-type size used, scale up

        elif len(nodeSizes)>0:          # if nodeSizes are given, use it
            
            if node in nodeSizes.keys(): # if this node is in nodeSizes, use the value
                nodesize=nodeSizes[node]
            else:
                nodesize=minnode        # otherwise use min value (e.g. if nodeSizes has only k>0 nodes,
                                        # and k=0 nodes from thresholding are shown too.
        else:
            if node in net:
                nodesize=A*strengths[node]+B
            else:
                nodesize=minnode

        if node in net:
            nodestrength=strengths[node]
        else:
            # This is for nodes which appear in MST coords (i.e. have
            # zero links) and are thus not included in net, but should
            # yet be displayed when visualizing a thresholded network
            nodestrength=mins     

        # Then determine color
        if coloredNodes:
            if setNodeColorsByProperty != None:
                # If setNodeColorsByProperty is given, use it initially
                value = net.nodeProperty[setNodeColorsByProperty][node]
                color = setColor(value,nodePropertyLimits,myNodeColorMap)

            if len(nodeColors)>0:
                # If dict nodeColors is given, it overrides
                # setNodeColorsByProperty
                if not nodeColors.get(node): 
                    # If node is not contained in dict nodeColors 
                    if setNodeColorsByProperty == None:
                        # Use setNodeColorsByProperty if it was given,
                        # otherwise use nodeColor and if it is not
                        # given use white.
                        color = (nodeColor or (1,1,1))

                else:
                    # If node IS contained in dict nodeColors, use
                    # nodeColors[node]
                    ctemp = nodeColors[node]
                    if len(ctemp)==6: 
                        # Recognize as Himmeli-type string ('999999')
                        rc=float(ctemp[0:2])/99.0
                        gc=float(ctemp[2:4])/99.0
                        bc=float(ctemp[4:6])/99.0

                        # this is a stupid hack; sometimes rounding
                        # errors result in rc=1.0 + epsilon and
                        # matplotlib complains...
                        rc = max(0.0, min(rc, 1.0))
                        bc = max(0.0, min(bc, 1.0))
                        gc = max(0.0, min(gc, 1.0))

                        color = (rc,gc,bc)
                    else:
                        # Otherwise assume it is an RGB tuple
                        color = nodeColors[node] 

            elif setNodeColorsByProperty is None and nodeColor is not None:
                # If neither setNodeColorsByProperty or dict
                # nodeColors is given, but nodeColor is, use nodeColor.
                if len(nodeColor)==6:

                    rc=float(nodeColor[0:2])/99.0
                    gc=float(nodeColor[2:4])/99.0
                    bc=float(nodeColor[4:6])/99.0

                    rc = max(0.0, min(rc, 1.0))
                    bc = max(0.0, min(bc, 1.0))
                    gc = max(0.0, min(gc, 1.0))

                    color=(rc,gc,bc)
                else:
                    color=nodeColor         

            elif setNodeColorsByProperty == None:
                # Set color by node strength
                color = setColor(nodestrength,(mins,maxs),myNodeColorMap) 
        else:
            # If coloredNodes is False, use white.
            color=(1.0,1.0,1.0)

        # Move node labels slightly to the right so that they
        # don't coincide on the nodes
        nodeLabel_xOffset = (nodeLabel_xOffset or float(nodesize)/40)

        plot_node(axes, x=xy[node][0], y=xy[node][1],
                  color=color, size=nodesize, edgecolor=nodeEdgeColor)

        if node in labels or uselabels == 'all':
            if node in labels:
                if isinstance(labels[node],float):
                    showthislabel="%2.2f" % labels[node]
                else:
                    showthislabel=labels[node]
            else:
                showthislabel = str(node)

            axes.annotate(showthislabel,(xy[node][0]+nodeLabel_xOffset,xy[node][1]),
                          color=fontcolor,size=fontsize)

    xylist = xy.values()
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

    if frame==True and showTicks==False:
        setp(axes,'xticks',[],'xticklabels',[],'yticks',[],'yticklabels',[])
    if not axisLimits==None:
        # If limits are given, use them, whatever the values of
        # showTicks or frame ...
        setp(axes,
             'xlim', (axisLimits[0][0],axisLimits[0][1]),
             'ylim', (axisLimits[1][0],axisLimits[1][1]))
    else:
        setp(axes,
             'xlim', (minx-xdelta,maxx+xdelta),
             'ylim', (miny-ydelta,maxy+ydelta))

    return thisfigure
            
# ---------------------------------------
              
class Himmeli:
    """ This class uses the executable Himmeli, which produces an .eps
    file AND outputs x-y-coordinates of nodes for visualization.
    """

    #---------------------------------------
    
    # First we have to find this executable
    if sys.platform=='win32':
        # For Win use direct path (probably works better with the
        # executable network toolbox...)
        himmeliExecutable="himmeli_3.0.1\himmeli.exe"
    else:
        # Trick: find out where netext.py is (must be in the netpython
        # directory), then add the rest of the path
        #himmeliExecutable = (os.path.dirname(netext.__file__)
        #                     +"/Himmeli/himmeli.exe")
        netext_path = os.path.dirname(netext.__file__) 
        himmeliExecutable = ("%s%s../himmeli_3.0.1/himmeli.exe" % 
                             (netext_path, ("/" if netext_path else "")))

        if not(os.path.isfile(himmeliExecutable)):
            # Just in case Himmeli was compiled without the .exe:
            #himmeliExecutable = (os.path.dirname(netext.__file__)
            #                     + "/Himmeli/himmeli")
            himmeliExecutable = ("%s%s../himmeli_3.0.1/himmeli" % 
                                 (netext_path, ("/" if netext_path else "")))

    # Directly complain if Himmeli not found.
    if not(os.path.isfile(himmeliExecutable)):
        complaint = ("Cannot find Himmeli! This is where it should be: "
                     + himmeliExecutable)
        raise Exception(complaint)

    # ----------------------------------------

    epsilon=0.0001 #hack, find the real thing

    def __init__(self, inputnet, time=20, configFile=None, threshold=None,
                 useMST=False, wmin=None, wmax=None, coloredNodes=True,
                 equalsize=True, nodeColor="999999", nodeSize="1.0",
                 coordinates=None, labels={}, distanceUnit=1, showAllNodes=True,
                 edgeLabels=False, nodeColors={}, treeMode=False):

        # inputs:
        # time - time limit (secs) for the Himmeli optimization of layout; for large nets, use higher values
        # configFile - Himmeli .cfg file, if you want to use a pre-existing one
        # threshold - for weighted nets; use only edges above this
        # useMST (true/false) : true - uses pre-calculated MST coords for the (weighted) net

        
        # Checking that the given net is valid and not empty
        #if net.__class__!=pynet.Net and net.__class__!=pynet.SymmNet:
        if not isinstance(inputnet,pynet.VirtualNet):
            raise AttributeError("Unknown net type "+str(inputnet.__class__))
        if len(inputnet._nodes) == 0:
            raise AttributeError("The net cannot be empty.")

        # Another EDEN-specific piece of code: if the network is a
        # distance matrix/network, first transform distances to
        # weights.
        if hasattr(inputnet,'matrixtype'):
            if inputnet.matrixtype==0:
                inputnet = transforms.dist_to_weights(inputnet)

        if wmin is None:
            # Finds out smallest and largest weight
            witer = inputnet.weights.__iter__()
            wmin = wmax = witer.next()

            for wt in witer:
                if wt < wmin:
                    wmin = wt
                if wt > wmax:
                    wmax = wt

        if showAllNodes:
            # This is especially designed for thresholded nets, where
            # there may be nodes with zero links in addition to
            # disconnected components. IF coordinates have been
            # calculated for the network WITHOUT THRESHOLDING,
            # augmentNet adds every node mentioned in coordinates to
            # the network (with epsilon-weight "ghost"
            # links). Furthermore, augmentNet joins all disconnected
            # components to the largest component with ghost links.
            net = self.augmentNet(inputnet,useMST,coordinates,wmin)

        else:
            net=inputnet

        if (showAllNodes or useMST):
            threshold2 = ['abs', wmin, wmax]

        #First we need to generate names for this net and its files
        rgen = random.Random()
        netName = str(rgen.randint(1,10000))
        edgFileName = "himmeli_tmp"+netName+".edg"
        confFileName = "himmeli_tmp"+netName+".cfg"
        vtxFileName = "himmeli_tmp"+netName+".vtx"
        coordFileName = netName+".vertices.txt"
        legendFileName = netName+".legend.eps"
        output_confFileName = netName+'.config.txt'
        output_edgFileName = netName+'.edges.txt'
        output_psFileName = netName+'.ps'

        #Then we make config for Himmeli or read it from a file
        if configFile==None:
            config = ("EdgeHeadVariable\tHEAD\n"
                      "EdgeTailVariable\tTAIL\n"
                      "EdgeWeightVariable\tWEIGHT\n"
                      "FigureLimit\t1\n"
                      "DecorationMode\ton\n"
                      "IncrementMode\ton\n")
            if treeMode:
                config += "TreeMode\ton\n"
            else:
                config += "TreeMode\toff\n"
            if coordinates==None:
                config += "TimeLimit\t"+str(time)+"\n"
            else:
                config += "TimeLimit\t0\n"
            if net.isSymmetric():
                config += "ArrowMode\toff\n"
            else:
                config += "ArrowMode\ton\n"
            #config += "PageSize\tauto\tauto\n"
            config += "PageSize\tauto\ta4\n"
            config += "DistanceUnit\t"+str(distanceUnit)+"\n"
            if len(labels)>0 and edgeLabels==False:
                config += "LabelMode\tvertex\n"
            elif len(labels)>0 and edgeLabels==True:
                config += "LabelMode\ton\n"
            else:
                config += "LabelMode\toff\n"
            #config += "PageOrientation\tportrait\n"
            if threshold != None:
                # Not tested properly (and everything else is?)
                filterType=threshold[0]
                minedge=threshold[1]
                maxedge=threshold[2]
                config += "EdgeWeightFilter\t"+filterType+"\t"
                config += str(0.99*minedge)+"\t"+str(1.01*maxedge)+"\n"
            if useMST or showAllNodes:
                filterType=threshold2[0]
                minedge=threshold2[1]
                maxedge=threshold2[2]
                config += "EdgeWeightMask\t"+filterType+"\t"
                config += str(0.99*minedge)+"\t"+str(1.01*maxedge)+"\n"

        else:
            configTemplate = open(configFile)
            config = configTemplate.read()
            configTemplate.close()

        #---These are specific for this Himmeli run
        config += "GraphName\t"+netName+"\n"
        config += "EdgeFile\t"+edgFileName+"\n"

        config += "VertexFile\t"+vtxFileName+"\n"
        config += "VertexNameVariable\tVNAME"+"\n"
        config += "VertexLabelVariable\tVLABEL"+"\n"

        if coloredNodes:
            config += "VertexColorVariable\tVCOLOR"+"\n"
        if equalsize:
            config += "VertexSizeVariable\tVSIZE\n"
        if coordinates!=None:
            config += "VertexXVariable\tVX\n"
            config += "VertexYVariable\tVY\n"

            #if showAllNodes:
            #    config += ("EdgeWeightMask\tabs\t"+str(2*self.epsilon)+"\t"
            #               +str(1/self.epsilon)+"\n")
            #    config += ("EdgeWeightFilter\tabs\t"+str(2*self.epsilon)+"\t"
            #               +str(1/self.epsilon)+"\n")

        #---

        # Now we write all nessesary files for Himmeli to disk edge
        # file:
        netio.writeNet(net,edgFileName,headers=True)

        # Vertex file:
        self.writeVertexFile(net, vtxFileName, coloredNodes, equalsize,
                             nodeColor, nodeSize, coordinates=coordinates,
                             labels=labels, nodeColors=nodeColors)
        # Config file:
        confFile=open(confFileName,'w')
        confFile.write(config)
        confFile.close()

        # All is set for running Himmeli
        himmeli = os.popen(self.himmeliExecutable+' '+confFileName,'r')
        #print string.join(himmeli.readlines()) #for long debug
        himmeli.close()

        #print himmeli #for short debug

        # Save coordinates produced by Himmeli
        self.coordinates = self._parseCoordinates(coordFileName)

        # Remove files that are not needed anymore
        os.remove(edgFileName)
        os.remove(confFileName)
        os.remove(coordFileName)
        if os.path.isfile(legendFileName):
            os.remove(legendFileName)
        os.remove(output_confFileName)
        os.remove(output_edgFileName)
        os.remove(output_psFileName)
        os.remove(vtxFileName)

        # Finally we save all the information needed later
        self.netName=netName

    def getCoordinates(self):
        return self.coordinates

    def saveEps(self,filename):
        shutil.copyfile(self.netName+"_0001.eps",filename)

    def draw(self):
        im = Image.open(self.netName+"_0001.eps")
        im.show()

    def _parseCoordinates(self, coordFileName):
        coordFile = open(coordFileName, 'r')
        coordFile.readline()
        coordinates={}
        for line in coordFile:
            columns=line.split("\t")
            if len(columns) == 13:
                # Previous version:
                #[comp,name,x,y,z,degree_in,dg_out,strengt_in,strength_out,
                # color,shape,size,label]=line.split("\t")
                name, x, y, z = line.split("\t")[1:5]
                if len(name) > 0:
                    try:
                        name = int(name)
                    except ValueError:
                        pass
                    coordinates[name] = tuple(map(float, (x,y,z)))
        return coordinates
        
    def _writeEpsilonEdges(self,net,fileName):
        """Obsolete! Replaced by augmentNet, which generates a new
        network with the epsilon edges directly added. No need for
        rewriting to any file; EdgeWeightFilter is always used.
        """
      #  with open(fileName,'a') as f:
      #      last=None
      #      for node in net:
      #          if last!=None:
      #             if net[last,node]==0:
      #                 file.write(str(node)+"\t"+str(last)+"\t"
      #                            +str(self.epsilon)+"\n")
      #          last=node
        pass

    def __del__(self):
        if os.path.isfile(self.netName+"_0001.eps"):
            os.remove(self.netName+"_0001.eps")
        
    def augmentNet(self, net, useMST=False, coords=None, wmin=None):
        """Make a network singly connected.

        If the network is singly connected, returns the network
        untouched. If not, connects one node of each component to the
        giant component with a very small weight and produces a list
        of these ghost edges. Alternatively, if `useMST` is True, all
        nodes which are keys in the coordinate list are added to the
        network, joined with epsilon edges.  This is useful for
        thresholding networks with various thresholds, so that even
        all k=0 nodes are always visible. 

        Returns augmented net with epsilon edges added.
        """
        # If min weight is not given, find it out
        if wmin is None:
            witer = net.weights.__iter__()
            wmin = witer.next()
            for wt in witer:
                if wt < wmin:
                    wmin = wt

        epsilon_factor = 25.0

        init_comp = percolator.getComponents(net)
        sizelist = [len(c) for c in init_comp]

        mc = max(sizelist)
        maxcomponent_index = 0
        for i, v in enumerate(sizelist):
            if v == mc:
                maxcomponent_index = i

        giantmembers = init_comp[maxcomponent_index]

        Ncomponents = len(init_comp)
        maxcomponent = len(giantmembers)

        # MAKE A COPY OF THE ORIGINAL NETWORK;
        #
        # deepcopy generated segfaults probably due to C++ interfacing
        # so this is simple and stupid (and slow). 

        N = len(net._nodes)

        if (isinstance(net,pynet.SymmFullNet)):
            newnet=pynet.SymmFullNet(N)
        else:
            newnet=pynet.SymmNet()
    
        for n_i, n_j, w_ij in net.edges:
            newnet[n_i][n_j] = w_ij

        # If MST not used, just connect all disjoint components.

        if useMST==False:
            if Ncomponents != 1:
                # Find out which component is the giant one
                # list its members for ghost edge targets.
                gianttemp = copy.deepcopy(giantmembers)

                giantmembers = []
                for i in range(0,len(gianttemp)):
                    giantmembers.append(gianttemp.pop())

                for index,c in enumerate(init_comp):
                    if index != maxcomponent_index:
                        ghostsource = c.pop()
                        tindex = int(math.ceil(random.random()*
                                               float(len(giantmembers)-1)))
                        ghosttarget = giantmembers[tindex]
                        newnet[ghostsource][ghosttarget] = wmin/epsilon_factor

        # Next, if useMST=True, use keys of coordinates to insert all
        # original nodes to the net, again with epsilon weights

        else:
            prevNode=None
            for newNode in coords.keys():
                if prevNode is not None:
                   if newnet[prevNode][newNode] == 0:
                       # JS 290509 changes [newNode,prevNode] to [newNode][prevNode]
                       newnet[newNode][prevNode] = wmin/epsilon_factor   
                prevNode = newNode

        return newnet


    def writeVertexFile(self, net, fileName, coloredNodes=True, equalsize=True,
                        singlecolor="999999", vcolors=0, singlesize="0.3",
                        coordinates=None, labels={}, nodeColors={}):
        with open(fileName, 'w') as f:

            if len(nodeColors) > 0:
                coloredNodes = True

            headers = ["VNAME", "VLABEL"]
            if coloredNodes:
                headers.append("VCOLOR")
            if equalsize:
                headers.append("VSIZE")
            if coordinates is not None:
                headers.append("VX")
                headers.append("VY")
            f.write("\t".join(headers) + "\n")

            for i in net:
                f.write(str(i))
                try:
                    f.write("\t"+str(labels[i]))
                except KeyError:
                    f.write("\t"+str(i))
                if coloredNodes:
                    if len(nodeColors)>0:
                        f.write("\t"+str(nodeColors[i]))
                    else:
                        f.write("\t"+singlecolor)
                if equalsize:
                    f.write("\t"+singlesize)
                if coordinates!=None:
                    f.write("\t"+str(coordinates[i][0]))
                    f.write("\t"+str(coordinates[i][1]))
                f.write("\n")

            
# ---------------------------------------
    
def drawNet(net,labels={},coordinates=None,showAllNodes=False):
    """Display a picture of the network using Himmeli
    """
    h=Himmeli(net, labels=labels, coordinates=coordinates,
              showAllNodes=showAllNodes)
    h.draw()


# ---------------------------------------        

# def shiftCoordinates(xy,nodelist,shift):
def shiftCoordinates(xy,nodelist, xshift=0, yshift=0, zshift=0):
    """Translate coordinates of given nodes. 
    
    Parameters
    ----------
    xy : dict
        A dictionary in which item 'node' is a tuple containing the
        coordinates of 'node'. They must contain either two or three
        elements, as in (x, y) or (x, y, z).
    nodelist : sequence
        Listing the subset of keys in xy that need to be translated
    xshift, yshift, zshift : float
        These values indicate how much to shift the coordinates. Each
        defaults to zero. If the coordinate list contains tuples of
        length two, zshift will be ignored.

    Return
    ------
    xy : dict
        The shifted coordinates.
    """
    
    for node in nodelist:
        coords = xy[node]
        if len(coords) == 2:
            xy[node] = (coords[0]+xshift, coords[1]+yshift)
        elif len(coords) == 3:
            xy[node]=(coords[0]+xshift, coords[1]+yshift, coords[2]+zshift)
        else:
            raise ValueError("The coordinate tuples must contain two or "
                             "three elements.") 
    return xy


def getWheelCoords(net, node, N_trys=1):
    """Return coordinates for a friend wheel."""
    
    def calculate_cost(loc, net):
        cost = 0
        for ni,nj,wij in net.edges:
            dist = np.abs(loc[ni] - loc[nj])
            cost += (min(dist, len(loc)-dist)-1)*wij
        return cost
            
    # Get the subnetwork spanned by the neighbours of `node`.
    neighbours = list(net[node])
    N = len(neighbours) # Includes also non-connected nodes.
    neighbour_net = transforms.getSubnet(net, neighbours)

    # There is nothing to optimize if N <= 3. Just return the obvious
    # answer.
    if N_all == 0:
        return {}

    if N >= 3:
        curr_res = (-1, {})
        for try_count in range(N_trys):
            # Go through all neighbouring nodes in a random order, switching
            # each to the best location, until no more change occurs.
            locs = dict(zip(neighbours, range(N)))
            rand_order = neighbours[:]
            changed = True
            while changed:
                changed = False
                np.random.shuffle(rand_order)
                current_cost = calculate_cost(locs, neighbour_net)
                for i, n_rand in enumerate(rand_order):
                    # Find the best location for n_rand.
                    current_loc = locs[n_rand]
                    best = (current_cost, n_rand)
                    for other in rand_order[:i]+rand_order[i+1:]:
                        new_locs = locs.copy()
                        new_locs[n_rand], new_locs[other] = new_locs[other], new_locs[n_rand]
                        new_cost = calculate_cost(new_locs, neighbour_net)
                        if new_cost < best[0]:
                            best = (new_cost, other)
                    if best[0] < current_cost:
                        locs[n_rand], locs[best[1]] = locs[best[1]], locs[n_rand]
                        current_cost = best[0]
                        changed = True

            if current_cost < curr_res[0] or curr_res[0] == -1:
                curr_res = (current_cost, locs)

        locs = curr_res[1] # Use the best result.

    # Optimal configuration found, calculate the coordinates on a
    # circle.
    coords = {}
    for n, loc in locs.iteritems():
        coords[n] = (np.cos(2*np.pi*loc/N_all), np.sin(2*np.pi*loc/N_all), 0.0)

    return coords

if __name__ == '__main__':
    """Run unit tests if called."""
    from tests.test_visuals import *
    unittest.main()
