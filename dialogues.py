"""

Collection of dialogue windows


"""

import pynet,os,netio,netext
import random
import heapq
import string
import percolator
import shutil
from PIL import Image
from math import ceil
from Tkinter import *

class MySimpleDialog(Toplevel):
    '''Master class for a dialog popup window.
       Functions body() and apply() to be overridden
       with whatever the dialog should be doing.'''

    def __init__(self,parent,title=None):

        Toplevel.__init__(self,parent)
        self.transient(parent)

        if title:
            self.title=title

        self.parent=parent
        self.result=None

        body=Frame(self)
        self.initial_focus=self.body(self,body)
        body.pack(padx=5,pady=5)

        self.buttonbox()
        self.grab_set()

        if not self.initial_focus:
            self.initial_focus(self)

        self.protocol("WM_DELETE_WINDOW",self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    def body(self,masterclass,masterwindow):
        pass

    def buttonbox(self):
        """OK and Cancel buttons"""

        box=Frame(self)
        w=Button(box,text="OK",width=10,command=self.ok,default=ACTIVE)
        w.pack(side=LEFT,padx=5,pady=5)
        w=Button(box,text="Cancel",width=10,command=self.cancel)
        w.pack(side=LEFT,padx=5,pady=5)

        self.bind("&lt;Return>",self.ok)
        self.bind("&lt;Escape",self.cancel)

        box.pack()

    def ok(self,event=None):

        if not self.validate():
            self.initial_focus.focus_set()
            return

        self.withdraw()
        self.update_idletasks()
        self.applyme()
        self.cancel()

    def cancel(self,event=None):

        self.parent.focus_set()
        self.destroy()

    def validate(self):
        return 1

    def applyme(self):
        pass

class WLogbinDialog(MySimpleDialog):
    """Asks for the number of bins for log binning
       and allows linear bins for 1...10"""


    def __init__(self,parent,title=None):

        Toplevel.__init__(self,parent)
        self.configure(bg='Gray80')
        self.transient(parent)

        if title:
            self.title=title

        self.parent=parent
        self.result=None
        self.linfirst=IntVar()
        self.numbins=StringVar()

        body=Frame(self,bg='Gray80')
        self.initial_focus=self.body(self,body)
        body.pack(padx=5,pady=5)

        self.buttonbox()
        self.grab_set()

        if not self.initial_focus:
            self.initial_focus(self)

        self.protocol("WM_DELETE_WINDOW",self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    def body(self,masterclass,masterwindow):

        self.b1=Checkbutton(masterwindow,text='Use linear bins for 1..10',variable=masterclass.linfirst,state=ACTIVE,bg='Gray80')
        self.b1.grid(row=0,column=0,columnspan=2)
        Label(masterwindow,text='Number of bins:',bg='Gray80').grid(row=1,column=0)
        self.c1=Entry(masterwindow,textvariable=masterclass.numbins,bg='Gray95')
        masterclass.numbins.set('30')
        self.c1.grid(row=1,column=1)
        return self.c1

    def applyme(self):
        self.result=[self.linfirst.get(),float(self.numbins.get())]

class AskNumberOfBins(MySimpleDialog):
    """Asks for number of bins for binning"""

    def __init__(self,parent,title=None):

        Toplevel.__init__(self,parent)
        #self.configure(bg='Gray80')
      #  self.transient(parent)

        if title:
            self.title=title

        self.parent=parent
        self.result=None
       # self.linfirst=IntVar()
        self.numbins=StringVar()

        body=Frame(self)
        self.initial_focus=self.body(self,body)
        body.pack(padx=5,pady=5)

        self.buttonbox()
        self.grab_set()

        if not self.initial_focus:
            self.initial_focus(self)

        self.protocol("WM_DELETE_WINDOW",self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    def body(self,masterclass,masterwindow):

       # self.b1=Checkbutton(masterwindow,text='Use linear bins for 1..10',variable=masterclass.linfirst,state=ACTIVE,bg='Gray80')
       # self.b1.grid(row=0,column=0,columnspan=2)
        Label(masterwindow,text='Number of bins:').grid(row=1,column=0)
        self.c1=Entry(masterwindow,textvariable=masterclass.numbins,bg='Gray95')
        masterclass.numbins.set('30')
        self.c1.grid(row=1,column=1)
        return self.c1

    def applyme(self):
        self.result=float(self.numbins.get())

class MatrixDialog(MySimpleDialog):
    """Used when loading a matrix. Asks if the matrix contains weights or distances"""
    

    def __init__(self,parent,title=None):

        Toplevel.__init__(self,parent)
        #self.configure(bg='Gray80')
      #  self.transient(parent)

        if title:
            self.title=title

        self.parent=parent
        self.result=None

        self.mattype=IntVar()
      
       # self.linfirst=IntVar()

        body=Frame(self)
        self.initial_focus=self.body(self,body)
        body.pack(padx=5,pady=5)

        self.buttonbox()
        self.grab_set()

        if not self.initial_focus:
            self.initial_focus(self)

        self.protocol("WM_DELETE_WINDOW",self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    def body(self,masterclass,masterwindow):

       # self.b1=Checkbutton(masterwindow,text='Use linear bins for 1..10',variable=masterclass.linfirst,state=ACTIVE,bg='Gray80')
       # self.b1.grid(row=0,column=0,columnspan=2)
        
        self.c1=Label(masterwindow,text='Matrix type:')
        self.c1.grid(row=0,column=0)

        r1=Radiobutton(masterwindow,text='Weight matrix',value=1,variable=masterclass.mattype)
        r2=Radiobutton(masterwindow,text='Distance matrix',value=0,variable=masterclass.mattype)
        r1.grid(row=0,column=1,sticky=W)
        r2.grid(row=1,column=1,sticky=W)
        
        masterclass.mattype.set(0)
       
        return self.c1

    def applyme(self):
        self.result=(self.mattype.get())

class MsatDialog(MySimpleDialog):
    """Used when loading a matrix. Asks if the matrix contains weights or distances"""
    

    def __init__(self,parent,title=None):

        Toplevel.__init__(self,parent)
        #self.configure(bg='Gray80')
      #  self.transient(parent)

        if title:
            self.title=title

        self.parent=parent
        self.result=None

        self.mattype=IntVar()
        self.dtype=IntVar()
      
       # self.linfirst=IntVar()

        body=Frame(self)
        self.initial_focus=self.body(self,body)
        body.pack(padx=5,pady=5)

        self.buttonbox()
        self.grab_set()

        if not self.initial_focus:
            self.initial_focus(self)

        self.protocol("WM_DELETE_WINDOW",self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    def body(self,masterclass,masterwindow):

       # self.b1=Checkbutton(masterwindow,text='Use linear bins for 1..10',variable=masterclass.linfirst,state=ACTIVE,bg='Gray80')
       # self.b1.grid(row=0,column=0,columnspan=2)
        
        self.c1=Label(masterwindow,text='Handling clones:')
        self.c1.grid(row=0,column=0)

        r1=Radiobutton(masterwindow,text='Collapse clones',value=1,variable=masterclass.mattype)
        r2=Radiobutton(masterwindow,text='Leave clones',value=0,variable=masterclass.mattype)
        r1.grid(row=0,column=1,sticky=W)
        r2.grid(row=1,column=1,sticky=W)

        self.c2=Label(masterwindow,text='Distance measure:')
        self.c2.grid(row=2,column=0)

        r3=Radiobutton(masterwindow,text='Linear Manhattan',value=0,variable=masterclass.dtype)
        r4=Radiobutton(masterwindow,text='Non-shared alleles',value=1,variable=masterclass.dtype)
        r5=Radiobutton(masterwindow,text='Allele parsimony',value=2,variable=masterclass.dtype)
        r3.grid(row=2,column=1,sticky=W)
        r4.grid(row=3,column=1,sticky=W)
        r5.grid(row=4,column=1,sticky=W)
        

        masterclass.dtype.set(1)    
        masterclass.mattype.set(1)
       
        return self.c1

    def applyme(self):
        self.result=[(self.mattype.get()),(self.dtype.get())]

        
class VisualizationDialog(MySimpleDialog):
    """Asks options for network visualization"""

    def __init__(self,parent,title=None):

        Toplevel.__init__(self,parent)
        #self.configure(bg='Gray80')
      #  self.transient(parent)

        if title:
            self.title=title

        self.parent=parent
        self.result=None

        self.winsize=IntVar()
        self.vtxsize=StringVar()
        self.vtxcolor=StringVar()
        self.bgcolor=StringVar()
       # self.linfirst=IntVar()

        body=Frame(self)
        self.initial_focus=self.body(self,body)
        body.pack(padx=5,pady=5)

        self.buttonbox()
        self.grab_set()

        if not self.initial_focus:
            self.initial_focus(self)

        self.protocol("WM_DELETE_WINDOW",self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    def body(self,masterclass,masterwindow):

       # self.b1=Checkbutton(masterwindow,text='Use linear bins for 1..10',variable=masterclass.linfirst,state=ACTIVE,bg='Gray80')
       # self.b1.grid(row=0,column=0,columnspan=2)
       
        self.c1=Label(masterwindow,text='Vertex color:')
        self.c1.grid(row=0,column=0)
        rowcount=-1
        for text, value in [('Black','000000'),('White','999999'),('Red','990000'),('Green','009900'),('Blue','000099'),('By strength','-1')]:
            rowcount+=1
            Radiobutton(masterwindow,text=text,value=value,variable=masterclass.vtxcolor).grid(row=rowcount,column=1,sticky=W)
        masterclass.vtxcolor.set('-1')
        Label(masterwindow,text='Vertex size:').grid(row=rowcount+1,column=0)
        for text, value in [('Small','0.4'),('Medium','0.7'),('Large','0.99'),('By strength','-1.0')]:
            rowcount=rowcount+1
            Radiobutton(masterwindow,text=text,value=value,variable=masterclass.vtxsize).grid(row=rowcount,column=1,sticky=W)
        masterclass.vtxsize.set('-1.0')
        Label(masterwindow,text='Show with:').grid(row=rowcount+1,column=0)
        for text, value in [('White background','white'),('Black background','black')]:
            rowcount=rowcount+1
            Radiobutton(masterwindow,text=text,value=value,variable=masterclass.bgcolor).grid(row=rowcount,column=1,sticky=W)
        masterclass.bgcolor.set('black')
        return self.c1

    def applyme(self):
        self.result=(self.vtxcolor.get(),self.vtxsize.get(),self.bgcolor.get())

class AskThreshold(MySimpleDialog):
    """Asks threshold for thresholding"""

    def __init__(self,parent,title=None):

        Toplevel.__init__(self,parent)
        #self.configure(bg='Gray80')
      #  self.transient(parent)

        if title:
            self.title=title

        self.parent=parent
        self.result=None
       # self.linfirst=IntVar()
        self.threshold=StringVar()

        body=Frame(self)
        self.initial_focus=self.body(self,body)
        body.pack(padx=5,pady=5)

        self.buttonbox()
        self.grab_set()

        if not self.initial_focus:
            self.initial_focus(self)

        self.protocol("WM_DELETE_WINDOW",self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    def body(self,masterclass,masterwindow):

       # self.b1=Checkbutton(masterwindow,text='Use linear bins for 1..10',variable=masterclass.linfirst,state=ACTIVE,bg='Gray80')
       # self.b1.grid(row=0,column=0,columnspan=2)
        Label(masterwindow,text='Threshold:').grid(row=1,column=0)
        self.c1=Entry(masterwindow,textvariable=masterclass.threshold,bg='Gray95')
        masterclass.threshold.set('0')
        self.c1.grid(row=1,column=1)
        return self.c1

    def applyme(self):
        self.result=float(self.threshold.get())
        
        
