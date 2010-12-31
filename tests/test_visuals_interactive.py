from Tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from netpython import *
n=pynet.SymmNet()
n[1,2]=1
n[2,3]=2
f=visuals.VisualizeNet(n,{1:(1,1),2:(1,2),3:(1,3)},interactive=True,uselabels='all')


w=Tk()
canvas=FigureCanvasTkAgg(f,master=w)
canvas.show()
canvas._tkcanvas.pack(side=TOP,fill=BOTH,expand=YES)
f.startInteraction()
mainloop()
