
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 18 21:26:53 2020

@author: thirschbuechler

this does not work properly and independently of scale, etc
todo: fix
    more elaborated: 
        - find annotate positions in absolute canvas coord
        - after drawing other data, make new layer
        - have scaling variable(s)

"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle
from scipy import interpolate

# my modules
from myink import myinkc as mc



class mc_circle(mc):        

    ## housekeeping
    def __init__(self, *args, **kwargs):
        #plt.close("all")
        # note: matplotlib may need to be reloaded to quit xkcd mode
        #importlib.reload(plt) # not required anymore (using with-context)
        self.ax = None
        self.fig = None
        
        self.pacmania=False#shall pacman markers be made    
        self.axdir="l"#default axis
        self.printimg=True#shall images be printed
        self.yright=None#var to be inspected on plot cleanup and reset

        super().__init__(*args, **kwargs) # superclass init, in case there is any


    def ann_circle(self, x, y, percx=33, orientation="r", scale=1, ax=None):
        #scale = (np.max(y)-np.min(y))/np.max(y)*0.1
        bwy = np.max(y)-np.min(y)
        ax = self.get_ax(ax)
        bwx = np.max(x)-np.min(x)
        
        scaley = bwy/bwx
        scalex = bwx/bwy
        
        markerx = percx/100*(np.max(x) - np.min(x))  + np.min(x)#where to put it along x-axis
        markery=self.interpoly(xaxis=x, yaxis=y, xasked=markerx)

        x = markerx # $$ todo refactor belwo
        y = markery
        print(y)
        
        # Configure circle
        center_x = x            # x coordinate
        center_y = y            # y coordinate
        
        radius_2 = bwx/5 * scaley           # radius 2 >> for cicle: radius_2 = 2 x radius_1 $$$$$$$$$$$$actually diameter wtf
        radius_1 = radius_2/4 *scalex        # radius 1 $$$$$$$$$$$$actually diameter wtf
        
        if orientation=="l":    # left, unusual
            angle = 180             # orientation
            sgn=-1
        else:
            angle=0
            sgn=1
            
        theta_1 = 70            # starts at this angle
        theta_2 = 290           # finishes at this angle
        circle = Circle([center_x, center_y],
                    radius_1,
                    capstyle = 'round',
                    linestyle='-',
                    lw=.1,
                    color = 'black',
                    fill=False)
        
        ax.add_patch(circle)
        
        # Add arrow
        x1 = x + 0.1 *sgn   *scalex          # x coordinate
        y1 = y + 0.2 *scaley              # y coordinate   
        
        length_x = sgn*0.5     # length on the x axis (negative so the arrow points to the left)
        length_y = 0        # 0 since horizontal
        ax.arrow(x1,
                    y1,
                    length_x,
                    length_y,
                    head_width=0.5*scaley,
                    head_length=0.05*scalex,
                    fc='k',
                    ec='k',
                    linewidth = 0.6*scaley)
        
            
    def ann_arc(self, x, y, percx=33, orientation="r", scale=1):
        ax = self.get_ax()
        bw = np.max(x)-np.min(x)
        markerx = percx/100*(np.max(x) - np.min(x))  + np.min(x)
        
        markery=self.interpoly(xaxis=x, yaxis=y, xasked=markerx)

        x = markerx # $$ todo refactor belwo
        y = markery
        
        # Configure arc
        center_x = x            # x coordinate
        center_y = y            # y coordinate
        
        #along y axis apparentlyax = self.get_ax()
        radius_2 = bw/5 * scale           # radius 2 >> for cicle: radius_2 = 2 x radius_1 $$$$$$$$$$$$actually diameter wtf
        #along x axis apparently
        radius_1 = radius_2/4         # radius 1 $$$$$$$$$$$$actually diameter wtf
        
        yscale=10*1E7
        radius_2 = bw/5 * scale /yscale
        
        if orientation=="l":    # left, unusual
            angle = 180             # orientation
            sgn=-1
        else:
            angle=0
            sgn=1
            
        theta_1 = 70            # arc starts at this angle
        theta_2 = 290           # arc finishes at this angle
        arc = Arc([center_x, center_y],
                    radius_1,
                    radius_2,
                    angle = angle,
                    theta1 = theta_1,
                    theta2=theta_2,
                    capstyle = 'round',
                    linestyle='-',
                    lw=1,
                    color = 'black')
        
        ax.add_patch(arc)
        
        # Add arrow
        x1 = x + 0.1 *sgn            # x coordinate
        y1 = y + 0.2              # y coordinate   
        
        length_x = sgn*0.5 *scale *100    # length on the x axis (negative so the arrow points to the left)
        length_y = 0        # length on the y axis
        ax.arrow(x1,
                    y1,
                    length_x,
                    length_y,
                    head_width=0.1*10,
                    head_length=0.05*scale,
                    fc='k',
                    ec='k',
                    linewidth = 0.6*10)
        
    
        #https://stackoverflow.com/questions/9850845/how-to-extract-points-from-a-graph
    def interpoly(self, xaxis, yaxis, xasked):    #xasked can be array or value to find y vals
        #xnew = np.linspace(xaxis.min(),xaxis.max(),300)
        heights_smooth = interpolate.splrep(xaxis,yaxis) #Use splrep instead of spline

        #splev returns the value of your spline evaluated at the width values.    
        return interpolate.splev(xasked, heights_smooth)


    def pacman_start(self):#startup pacman markers aka circle pointers BEFORE plotting
        self.pacmania=True    
        

    def pacman_worker(self, ax=None):
        #print("working..")
        if self.pacmania:
            ax=self.get_ax(ax)#twinx also puts itself there so no switch necessary - #is it? route trough
            #print("working jarder..")
            #if self.axdir=="l":#default, grab left ones
            #    ax=self.get_ax()
            #else:
            #    ax=self.axtwin # get other handle
            #print(ax.lines)                
            for line in ax.lines:
                #print("hello")
                x,y = line.get_xdata(), line.get_ydata()
                #print(x)
                #print(y)
                #ylabel=ax.get_ylabel()
                #if ylabel.index("dB")>0:
                #    y = np.power(10,y/10)
                #    print("hi")
                #    print(y)
                self.ann_circlex(x,y,25, scale=0.5, orientation=self.axdir, ax=ax)       
            
        
    #def pacman_janitor(self,x,y,orientation="r"):#call packman in custom plots at end
    #    pass    
    

                
#-#-# module test #-#-#
if __name__ == '__main__': # test if called as executable, not as library
    ele = mc_circle()

    print(ele.defaultcolorlist())

    x = np.array([0, 1, 2, 5])
    y = np.array([-1, 0.2, 0.9, 2.1])

    k, d = ele.LSQ(x,y)

    #ele.subplots()
    #ele.plot()#this is in thvsia
    plt.plot(x, y, 'o', label='Original data', markersize=10)
    #plt.plot(x, k*x + d, 'r', label='Fitted line', c=ele.defaultcolorlist())

    ele.ann_circle(x,y,25, scale=0.5, orientation="r")       

    plt.legend()
    plt.show()