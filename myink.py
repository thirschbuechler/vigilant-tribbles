
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Myink

Provide an abstract layer to matplotlib

- Handle cycling through plots and keep track of axes
- Souped-up plot functions
- Some image handling
- Some logging
- Routed-through bare-metal access


Created on Mon May 18 21:26:53 2020
@author: thirschbuechler
"""
import colored_traceback.always # colorize terminal output and errors in terminal and vscode terminal
from logging import exception
import re
import os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import EngFormatter, LogFormatterSciNotation, ScalarFormatter #enginerd stuff
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter) # nicergrid
from matplotlib.ticker import PercentFormatter # histo percent
from matplotlib.transforms import Bbox
from matplotlib.patches import Rectangle


try:
    import mystring as ms
    import hopper as hoppy
    import mailuefterl as ml
    import cal_plot_corr_mx as cplm
except:
    try:
        import vigilant_tribbles.mystring as ms
        from vigilant_tribbles import hopper as hoppy
        import vigilant_tribbles.mailuefterl as ml
        import vigilant_tribbles.cal_plot_corr_mx as cplm

    except:
        print("failed to import module directly or via submodule -  mind adding them with underscores not operators (minuses aka dashes, etc.)")

modulepath = (os.path.dirname(os.path.abspath(__file__)))

#from matplotlib.patches import Arc, Circle

#from PIL import Image # pillow library --> MOVED DOWN TO IMPORT SWITCH
#import cv2 # python-opencv library - linux:pip install opencv-python --> MOVED DOWN TO IMPORT SWITCH

#from skimage import idata, icolor
#from skimage.transform import rescale, resize, downscale_local_mean


figsizes = {"deffig":[6.4, 4.8], "bigfig":[15,10], "medfig":[10,6.6], "widefig" : [2*6.4, 4.8], "tallfig" : [6.4, 2*4.8], "dwarffig" : [6.4, 4.8/2]}
fontsizes = {"deffig":3, "bigfig":5, "medfig":4, "widefig":4, "tallfig":4, "dwarffig":3}
#uni_angle = '\U00002222'


# ToDos myink general
# - see littered to-dos / to-do tree

# my modules
#-#-# module test #-#-#
testing=False # imports don't seem to traverse this before reaching EOF and complaining about undef_bool !?
if __name__ == '__main__': # test if called as executable, not as library
    
    testing=True
    #tester()#since this is no fct definition, can't call this, also py has no forward-declaration option
else:
    pass

    #testing=False

class gradientmaster(object):

    def __init__(self, datalen = None, cmap = plt.cm.turbo, gradientplot=True, monocolor=False):
        #n = len(datas)
        if not datalen:
            raise Exception("gradientmaster needs datalen!")

        if gradientplot:
            import matplotlib.pyplot as plt
            # 0.1-0.9 to avoid dark brown/black edges with look the same
            colors = cmap(np.linspace(0.1,0.9,datalen)) 
        elif monocolor:
            colors =  ["black" for i in range(0,datalen)]
        else:
            #colors = None
            colors = []
            pass

        self.colors = (colors)

    def cycle(self, i):
        if len(self.colors):
            return self.colors[i]
        else:
            return None


## thing to make matplotlib access easier ###
class myinkc(hoppy.hopper): 
    
    def __init__(self, tikz=False, *args, **kwargs):
        """ init some vars, mostly passing args to superclass """
        # note: matplotlib may need to be reloaded to quit xkcd mode
        # importlib.reload(plt) # not required anymore (using with-context)
        self.ax = None
        self.twins = []
        self.fig = None
        self.subplot_counter = 0
        self.outputformat = "png"
        self.tex = 0
        self.rc_autoreset = 0
        self.close_after_savefig = 0
        self.figs_dir = "figs_out" # outputdir - lies in current path!! e.g. modified by hopper(), portal() or thereof
        
        self.imims=[] # remember imageshows for rescaling - common_cb_lims

        self.printimg=True # shall images be printed
        self.yright=None # var to be inspected on plot cleanup and reset

        self.log=None # HACK

        kwargs = self.mycanvassize(**kwargs)
        
        super().__init__(*args, **kwargs) # superclass init, in case there is any

        if tikz:
            self.tikz_enable()


    def mycanvassize(self, **kwargs):
        """ if one of the keys (e.g. medfig) is set (e.g. medfig=True) in kwargs:
            - get kwargs
            - adjust canvas/subplots
            - pop used parameters
            - return kwargs without used params
                (for further __init__ processing)
            """

        
        for key in figsizes.keys():
            if key in kwargs:
                self.canvas_params(fontsize=fontsizes[key],figsize=figsizes[key])
                kwargs.pop(key)

        # sometimes canvassize is only closed after plotting once,
        # so open and close a sacraficial dummy plot
        fig, ax = self.subplots()
        self.plot()
        self.close(fig)
        #self.close("")# == self.close("all") # nuked waterfall etc.

        return kwargs


    def tikz_enable(self):
        plt.style.use("ggplot")
        self.outputformat = "tikz"


    def tikz_save_lastgraph(self, fn=""):
        """ legacy fct for save-lastgraph in case of tikz_enable() called"""
        self.save_lastgraph(fn=fn)


    def save_lastgraph(self, fn=""):
        """ save last graph as png or tikz """
        # filename init #
        if not fn:
            if self.current_suptitle:
                fn = self.current_suptitle
            elif self.current_title:
                fn = self.current_title
            else:
                raise Exception("no title to use")
        
        # filename massaging
        fn = self.sanitize(fn)
        dir = self.figs_dir
        os.makedirs(dir, exist_ok=True)
        fn = os.path.join(dir,fn)

        # save #
        if self.outputformat=="tikz":
            fn = "{}_{}.tex".format(fn, self.subplot_counter)
            # pyright, pylance: ignore import error on module not present
            import tikzplotlib # type: ignore
            tikzplotlib.save(fn)
            print("tikz saved {} in {}".format(fn, self.getpath() ) )
            #self.subplot_counter+=1 # nope subplots does tha
        #elif self.outputformat=="png":
        else:
            # assume png, svg, pdf, .. (something mpl can do) is chosen
            fn = "{}.{}".format(fn,self.outputformat)
            self.savefig(fname=fn, format=self.outputformat, pad_inches=0)
            """ forwarder to mpl
                savefig(
                    fname, *, dpi='figure', format=None, metadata=None,
                    bbox_inches=None, pad_inches=0.1,
                    facecolor='auto', edgecolor='auto',
                    backend=None, **kwargs)
            """
        
        # optional cleanup
        if self.close_after_savefig:
            self.close()
                    

    def saveallfigs(self, fns=[]):
        figs = list(map(plt.figure, plt.get_fignums()))
        if not figs:
            raise Exception("no figs retrieved to save, there are none!")
        
        # case filenames given
        if fns:
            if len(fns) == len(figs):
                for fig, fn in zip(figs, fns):
                    plt.figure(fig)
                    self.save_lastgraph(fn)
            else:
                raise Exception(f"figure savenames:{len(fns)} != available figures:{len(figs)}")
        
        # case no filenames - take titles, suptitles or whatever
        else:
            plt.figure(fig)
            self.save_lastgraph()


    def postprocess_figs(self, cmd):
        """ execute shell cmd in self.figs_dir
        
        eg: imagemagick convert to remove borders
            cmd = "for f in *.png; do convert $f -trim +repage $f; done"
        """
        import subprocess
        with hoppy.hopper(self.figs_dir):
            # todo - stdout=PIPE or sth to get useful return value
            self.log.trail("postprocessing..")
            proc = subprocess.Popen(cmd, shell=True)
            proc.wait() # ensure it's done before continuing
            self.log.trail("postprocessing done!")
        
    def subplots(self, *args, **kwargs):
        """ make subplot axes (plt.subplots(..)) and save axs for iterating via fct
            - ax_onward
            - ax_backtrack
            - ax_move(int) #relative
            """

        if self.rc_autoreset:
            # set medfig, bigfig or any other figsize right after subplots() init per graphset,
            # and use this to make next ones default to default automatically
            self.canvas_params_reset()

        # # cleanup last graph  # #
        # save tikz if enabled #
        if self.outputformat=="tikz": # if enabled - save here and with self.show()
            if self.subplot_counter>0: # not first one and var created by enabling
                self.tikz_save_lastgraph()
        # cleanup tikz vars #
        self.current_suptitle = ""
        self.current_title = ""

        # # new graph # #
        self.fig, self.axs = plt.subplots(*args, **kwargs)
        
        # save properties #
        self.ax_i = 0
        self.subplot_counter+=1

        if not (hasattr(self.axs, "__iter__")):#case axs was ax only #np.size didn't work for 2d axs
            self.ax=self.axs#put singular here    
            self.axs=np.array([self.axs])# axs list here - enable parsing always
        
        else: # case axs is list already
            self.axs=self.roadkill(self.axs) #remove any dimensions    
            self.ax=self.axs[0]
            
        return self.fig, self.axs
    
    
    def close(self, st="all"):
        """ close plots
        - default: all
        - "": close last one
        - "emptyax": close current plot if ax empty

        CAVEAT: only works on current session (jupyter-section, terminal, ..)
        """
        
        # define log thingy # HACK shouldnt be here
        if self.log:
            out=self.log.trail
        else:
            out=print

        # get and try to close
        if st=="emptyax":
            ax = self.get_ax()
            if ax:
                if not(ax.lines or ax.collections):
                    fig = self.get_fig()
                    
                    title = ax.get_title()
                    if not title:
                        title = "(empty figure title)"
                    out(f"closing \' {title}\'")
                    plt.close(fig)
        else:
            plt.close(st)


    def show(self):
        """ show last plots - for non-spyder IDEs which need manual trigger """
        if self.outputformat=="tikz": # if enabled
            self.tikz_save_lastgraph()

        plt.show()
    
    
    def rcparams_update(self,dict):
        plt.rcParams.update(dict)
        #e.g. this as
        #plt.rcParams.update({'font.size': 22})
        #self.rcparams_update({'font.size': 22})
    
    def canvas_params(self,fontsize=5,figsize=[15,10], dpi=300):
        """ takes fontsize in pt,  figsize-list in cm, and dpi
            e.g.
            - fontsize=5
            - figsize = [15,10]
            - dpi = 300
        """
        cm = 1/2.54
        self.rcparams_update({'font.size': fontsize, 'figure.figsize': np.array(figsize)*cm, 'figure.dpi': dpi})
    
    def canvas_params_reset(self):
        """ reset canvas_params to what is default, according to internet
            e.g. for a small plot to not look ugly and stretched
        """
        #self.rcparams_update({'font.size': 10, 'figure.figsize': [6.4, 4.8], 'figure.dpi': 100})
        self.rcparams_update(mpl.rcParamsDefault)


    def savefig(self,*args, **kwargs):
        """ forwarder to mpl
                savefig(
                    fname, *, dpi='figure', format=None, metadata=None,
                    bbox_inches=None, pad_inches=0.1,
                    facecolor='auto', edgecolor='auto',
                    backend=None, **kwargs)
        """
        plt.savefig(*args, **kwargs)


    def ax_onward(self):
        """ move to next subplot axis """
        self.ax_move(1)
        return self.ax
        
    
    def ax_backtrack(self):
        """ move to prev subplot axis """
        self.ax_move(-1)
        return self.ax
    
    
    def roadkill(self, *args, **kwargs):
        return ml.roadkill(*args, **kwargs)
    
    
    def ax_move(self, where):
        """ move relative up/down to another subplot axis """
        self.ax_i = self.ax_i + where
        
        self.axs = self.roadkill(self.axs)
        
        if np.size(self.axs)==0:
            raise Exception("only one axis - can't iterate")
        self.ax = self.axs[self.ax_i]
        return self.ax
    
    

    def get_ax(self, ax=None): 
        """ get class' ax or check if ax is passed and route through 
        
            function, since pos in axs will change during plotting
            !! generates figure if none (no plt.figure() or self.subplots() etc. called beforehand)!! ergo be inside doplot()-if-context
        """
        if ax is None: # no axis given
            if type(self.ax) is type(None): # is axis not a property already - robust
                ax=plt.gca() #  get current axis $$ this might give multiple.. wtf$$ no the error was probably self.ax=self.axs[0] above
                #print("gca")
            else:    
                ax=self.ax # if its a property take that
                #print("returning directly")
        return ax
    
    
    def set_ax(self, ax=None):
        """ set class' ax via parameter or matplotlib poll """
        if ax is None: # no axis given
            self.ax=plt.gca() #  get current whatever
        else:
            self.ax=ax
    
    
    def get_fig(self, fig=None):
        """ get class' fig or check if fig is passed and route through
        """
        if fig is None: # no axis given
            if type(self.fig) is type(None): # is axis not a property already - robust with type
                fig=plt.gcf() #  get current whatever $no setting - does it matter
            else:    
                fig=self.fig # if its a property take that
        return fig
    
    
    def set_fig(self, fig=None):
        """ set class' fig via parameter or matplotlib poll
        """
        if fig is None: # no figis given
            self.fig=plt.gcf() #  get current whatever
        else:
            self.fig=fig
    
    
    def twinx(self, ax=None):
        """ dual use of x-axis generates y label and ticks on right """
        ax = self.get_ax(ax)
        #pos = int(np.where (self.axs == ax)[0]) # integer of first occourance
        
        ax = ax.twinx()
        #self.axs = np.insert(self.axs, pos+1, ax) # insert new ax after # CANNOT - this breaks the plot, as any ax inserted changes layout
        #self.ax_i = self.ax_i+1 # count to new
        self.ax = ax # take new
        self.twins.append(self.ax)
        #self.ax_onward()

    
    def twiny(self, ax=None):
        """ dual use of y-axis generates x label and ticks on top """
        ax = self.get_ax(ax)
        #pos = int(np.where (self.axs == self.ax)[0]) # integer of first occourance
        self.ax = ax.twiny()
        self.twins.append(self.ax)
    
    
    def suptitle(self, title=""):
        """ major title/label for figure == "supertitle", to be fig.suptitle compatible 
            alias figlabel
            """
        fig = self.get_fig()
        fig.suptitle(title)
        self.current_suptitle = title
        
    
    def figlabel(self, title=None):
        """ alias suptitle """ 
        if title!=None:    
            self.suptitle(title)
            
    
    def title(self, title=None): 
        """ minor title of individual axis
            
            (major one - figlabel)
            """
        ax = self.get_ax()    
        if title!=None:    
                ax.set_title(title)
                self.current_title = title
        
    def axlabel(self, title=None): 
        """  alias title """
        self.title(title)

    def set_figlabel(self, *args, **kwargs):
        self.figlabel(self, *args, **kwargs)
    
    
    def get_figlabel(self):
        fig = self.get_fig()
        if type(fig._suptitle) == type(None):#if it doesn't exist
            return fig._suptitle
        else:
            return ""
        
        
    def enginerd_xaxis(self, ax=None, unit='Hz', **kwargs):
        ax = self.get_ax(ax)
        self.enginerd_axis(ax.xaxis, unit=unit, **kwargs)
        

    def enginerd_yaxis(self, ax=None, unit='Hz', **kwargs):
        ax = self.get_ax(ax)
        self.enginerd_axis(ax.yaxis, unit=unit, **kwargs)        
        

    def enginerd(self, value, unit='', places=2, sep="\N{THIN SPACE}", text=True, **kwargs): #u2009 thinspace not nice in tex, also "G" in graph and Hz in label == unprofessional -_-
        """ return engineer-nerd formatted string for a given float
            optional:
            - places : how many decimals (default = 2)
            - unit (str t append)
            - sep: separator (str, default Unicode-thin-space, non-ascii!)

            # https://matplotlib.org/3.1.0/gallery/text_labels_and_annotations/engineering_formatter.html
            
            name is pun on engineer-nerd
        """
        if self.tex:
            sep = r"$\thinspace$"
        if text==True:
            return(EngFormatter(places=places, sep=sep, **kwargs).format_eng(value)+unit)
        else:
            if not self.tex:
                return(EngFormatter(places=places, sep=sep, **kwargs))
            else:#places=places, sep=sep, 
                #return(LogFormatterSciNotation(**kwargs))
                return(ScalarFormatter(**kwargs)) # eg puts 10E9 on right
                
                


    
        
    def enginerd_axis(self, axissub="", **kwargs):
        """ set enginerd formatter for a axis"""

        if axissub=="":
            #axissub=plt.gca().xaxis # as default param, this would create
            #  an empty fig on importing, even without an obj instance
            raise exception("Specify axis for enginerd format!")
        
        axissub.set_major_formatter(self.enginerd(text=False, value=None, **kwargs))
    
    
    def killlegend(self,ax=None):
        ax = self.get_ax(ax)
        oh_my = ax.get_legend()
        if oh_my:
            oh_my.remove()


    def yticklabels(self, stuff, **kwargs):
        self.get_ax().set_yticks(range(0,len(stuff)))
        self.get_ax().set_yticklabels(stuff, **kwargs)

    def xticklabels(self, stuff, **kwargs):
        self.get_ax().set_xticks(range(0,len(stuff)))
        self.get_ax().set_xticklabels(stuff, **kwargs)


    def killxlabel(self):
        self.xticklabels("") # remove numbers
        self.xlabel() # remove text (unit)
        
    def legend(self, **kwargs):
        """ forward to mpl legend
            - handles (lines)
            - labels
            - bbox_to_anchor, loc, borderaxespad, ..
        """
        ax = self.get_ax()
        ax.legend(**kwargs)


    def modlegend(self, mylegendtext=None, addtext=None, title=None, rmsubstr=None, ax=None, *args, **kwargs):#, *args, **kwargs for ax.legend only
        """ OLD - h,l = get_legend_handles_labels() is kinda better
            legend handler and creator 
            - create out of self.mylegend if no mylegendtext passed 
            - use mylegendtext (if passed and same len)
            - remove shit with rmsubstr
            - DOES NOT WORK FOR plot, as it does not save mylegendtext
            """
        # addtext is a list of same len as legend    
        ax = self.get_ax(ax)
        
        if mylegendtext!=None: 
            if len(mylegendtext)>0:
                
                self.killlegend(ax)# remove current stuff
                
                # differentiate for strings / lists
                if type(mylegendtext)==str:
                    ax.text(1, 0, mylegendtext,
                            verticalalignment='bottom', horizontalalignment='right',
                            transform=ax.transAxes) # transform means koord sys of graph, not data
                    # todo: maybe more options from https://matplotlib.org/3.1.1/tutorials/text/text_intro.html
                elif type(mylegendtext)==list:
                    ax.legend(mylegendtext, *args, **kwargs)
                else: # complain
                    mylegendtext="unknown legend text type: " + type(mylegendtext)
                    ax.text(1, 0, mylegendtext,
                            verticalalignment='bottom', horizontalalignment='right',
                            transform=ax.transAxes) # transform means koord sys of graph, not data
                    # todo: maybe more options from https://matplotlib.org/3.1.1/tutorials/text/text_intro.html
        
        elif type(addtext)!=type(None):#check type to avoid elementwise
            ll=list(ax.get_legend().get_texts()) # fetch what is there
            texts = [item._text for item in ll ]
            mylegendtext=texts
            #print(texts)
            texts = [ texti+str(addi) for texti,addi in zip(texts,addtext)]
            #    note: only goes as far as lowest itemcount, see
            #   [(xi+xu) for xi,xu in zip(np.ones(2), np.zeros(5))]
            ax.legend(texts)
            
        if title!=None:
            #print(title)
            from matplotlib.patches import Rectangle 
            #https://stackoverflow.com/questions/16826711/is-it-possible-to-add-a-string-as-a-legend-item-in-matplotlib
            
            ll=list(ax.get_legend().get_texts()) # fetch what is there
            texts = [item._text for item in ll ]
            mylegendtext=texts
            
            extra = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0) # dummy rect
            
            mytext=mylegendtext
            
            ## todo: outsource it into  "turn into list" function
            if type(mytext)==list:
                pass # we're good
            elif type(mytext)==type(np.ones(1)):#numpy ndarray          
                mytext=list(mytext)
            elif type(mytext)==str:
                mytext=[mytext]
            else:
                mytext=[str(mytext)]#assume int, float, ..
            
            
            if rmsubstr!=None:
                mytext=ms.removestringparts(rmsubstr,mytext)
                print(mytext)
                
            mytext.insert(0,title) # insert as first ele into list
            legendlines=ax.get_lines()[:] # decompose simple_list object, or sth.
            legendlines.insert(0,extra) # insert into regular list
            
            
            #print(mytext)
            #print()
            
            ax.legend(legendlines, mytext)   
    

    def comradekernel(self, **kwargs):
        """ common for comradelegend, comradeaxlegend"""
        
        fig = self.get_fig()#fetch
        
        # fuckin' babysit legend placing...
        yoff = 0.12 # empirical 
        xoff = 0.11
        if "outside" in kwargs:
            if kwargs["outside"]:
                yoff = 0 # would place it diagonally outside ON FULLSCREEN FIG ONLY $$todo: get dependent on size? aaa
                xoff = 0
            kwargs.pop("outside") # don't pass downstream matplotlib
        
        if "loc" in kwargs:

            if kwargs["loc"]=='lr': # lowerright
                kwargs1=dict(bbox_to_anchor=(1-xoff, yoff), loc='lower right', borderaxespad=0.)
            
            elif kwargs["loc"]=='ll': # lowerleft
                kwargs1=dict(bbox_to_anchor=(xoff+0.025, yoff), loc='lower left', borderaxespad=0.)
                
            elif kwargs["loc"]=='ul': # upperleft
                kwargs1=dict(bbox_to_anchor=(xoff+0.025, 1-(yoff+0.01)), loc='upper left', borderaxespad=0.)
                
            elif kwargs["loc"]=='ur': # upperright
                kwargs1=dict(bbox_to_anchor=(1-xoff, 1-(yoff+0.01)), loc='upper right', borderaxespad=0.)

            # center - of figure not current ax :( - and variants
            elif kwargs["loc"]=='c': 
                kwargs1=dict(bbox_to_anchor=[0.5, 0.5], loc='center', borderaxespad=0.)

            elif kwargs["loc"]=='cr': # center right
                kwargs1=dict(bbox_to_anchor=[0.75, 0.75], loc='center', borderaxespad=0.)

            elif kwargs["loc"]=='cl': # center left
                kwargs1=dict(bbox_to_anchor=[0.25, 0.25], loc='center', borderaxespad=0.)
            
            elif type(kwargs["loc"])==type([1,2]):
                kwargs1=dict(bbox_to_anchor=kwargs["loc"], loc='center', borderaxespad=0.)
                
            else:
                print("programmer, you screwed up.")
                os.close(0)
            
            # in any case:
            kwargs.update(kwargs1)
        
        if not("handles" in kwargs and "labels" in kwargs):
            # collect old legends
            #https://stackoverflow.com/questions/9834452/how-do-i-make-a-single-legend-for-many-subplots-with-matplotlib
            lines_labels = [ax.get_legend_handles_labels() for ax in fig.axes]
            handles, labels = [sum(lol, []) for lol in zip(*lines_labels)]
            kwargs["handles"] = handles
            kwargs["labels"] = labels
        else:
            # pass them through - do nothing
            pass

        # kill old legends
        for ax in fig.axes:
            self.killlegend(ax)

        return kwargs


    def comradelegend(self, fig=None, **kwargs): 
        """ collect all labels of one Figure and collate to one master legend 
            locations "loc": 
                - upper/lower left/right/center - equals
                - loc="ul/ll/lr/ur/c"
        """
        fig = self.get_fig(fig)#fetch
        kwargs = self.comradekernel(**kwargs)
        fig.legend(**kwargs)
        
        
    def comradeaxlegend(self, ax=None, **kwargs):
        """ collect all labels of one Axis and collate to one master legend,
            same params as comradelegend    
        """
        ax = self.get_ax(ax)
        fig = self.get_fig(fig)#fetch
        kwargs = self.comradekernel(**kwargs)
                
        # finally we invoke the legend (that you probably would like to customize...)
        ax.legend(**kwargs)


    def make_legend_scrollbar(self, ax=None):
        """ add an invisible scrollbar to the legend
            - ax: axis to fetch legend from (optional)
        """
        legend = self.get_ax(ax).get_legend()
        fig = self.get_fig()

        # pixels to scroll per mousewheel event
        d = {"down" : 30, "up" : -30}

        def func(evt):
            if legend.contains(evt):
                bbox = legend.get_bbox_to_anchor()
                bbox = Bbox.from_bounds(bbox.x0, bbox.y0+d[evt.button], bbox.width, bbox.height)
                tr = legend.axes.transAxes.inverted()
                legend.set_bbox_to_anchor(bbox.transformed(tr))
                fig.canvas.draw_idle()

        fig.canvas.mpl_connect("scroll_event", func)
    

    # oszi-like markers, buy one get two! limited offer!!
    def vmarkers(self, start, stop, ax=None, col="black", linestyles="solid"):
        """ oszi like vertical cursors """
        ax = self.get_ax(ax)
        ylims=ax.get_ylim()
        ax.vlines(start,  ylims[0], ylims[1], colors=col, linestyles=linestyles)
        ax.vlines(stop,  ylims[0], ylims[1], colors=col, linestyles=linestyles)
        

    def hmarkers(self, start, stop, ax=None, col="black", linestyles="solid"):
        """ oszi like horizontal cursors"""
        ax = self.get_ax(ax)
        xlims=ax.get_xlim()
        ax.hlines(start,  xlims[0], xlims[1], colors=col, linestyles=linestyles)
        ax.hlines(stop,  xlims[0], xlims[1], colors=col, linestyles=linestyles)
        

    # mixture of keyworded and non-keyworded arguments, aswell as routing not everything through makes this not practical
    # does what it says on the tin -- 
    #  $todo: if figure creation happens in thsmith via fct, has to be triggered as well         
    #def xkcd_ify(self, fct=plt.plot, *args, **kwargs):
    #    with plt.xkcd():
    #       fct(*args, **kwargs)


    def bug(self,title="bug"):
        self.subplots()
        with hoppy.hopper(modulepath):
            if os.path.exists("myfigures/stinkbug.webp"):
                from PIL import Image
                # using PIL
                self.imshow(Image.open("myfigures/stinkbug.webp"))
        self.blank()
        self.title(title)


    def markernum(self, num):
        """" marker helper - skip first two horz matplotlib markers unless too many
        
            returns: int for marker: 2-11

            can be passed as "marker=self.markernum(i)" to matplotlib fcts
        """
        num=num+2 # 
        while(num>11): # ensure matplotlib markers don't overflow
            num=num-12
        return num
    
    
    def del_nonnum(self, a):
        return re.sub('[^0-9.]','', a)
    

    def killall(self):
        plt.close("all") # fun but not needed
    
    
    def LSQ_line(self, x, y):
        """ THE OLD FASHIONED MOORE PENROSE WAY"""
        # make pinv basis
        A = np.vstack([x, np.ones(len(x))]).T
        # make pinv and unpack
        k, d = np.linalg.lstsq(A, y, rcond=None)[0]
        
        return k,d
    
    
    def get_points(self):
        return self.list_to_xy (self.points)
    

    def list_to_xy(self, mylist):
        
        if type(mylist)==list:# should be [[x1,,y1], [x2, y2]]rcParams["axes.prop_cycle"]
            
            b = np.matrix(mylist)
            x,y = b.T
            x = np.array(x)[0] # remove extra dim from list
            x = x.astype("float")
            y = np.array(y)[0]
            y = y.astype("float")
            
            return x,y

        else:
            raise Exception("something fucked up - points are no list in list_to_xy")
        

    def resetcolorwheel(self):
        """ restart auto-"colorwheel" for line-colors """
        self.get_ax().set_prop_cycle(None)
        

    def defaultcolorlist(self, maxval=""):
        dictlist=[]
        for value in list(plt.rcParams["axes.prop_cycle"]):
            dictlist.append(value["color"])

        if maxval!="":
            while len(dictlist) > int(maxval):
                dictlist.pop()
    
        return dictlist
    
    
    def include_me(self, left, right, me):
        """ include a value (me) into a boundary (left, right) by rewriting it (coeff 1.1)

        get two bound and tertiary value, if third out of bounds include the third

        # example use
        left, right = ax.get_xlim() 
        left, right = self.include_me(left, right, 0)
        ax.set_xlim(left, right)
        """
        
        if me < left:
            left=me*1.1
        elif me > right:
            right=me*1.1
            
        return left, right
    

    def picframe(self, *args, **kwargs): # unused atm, maybe into picshow at some time
        kwargs["dpi"]=300
        return self.subplots(*args, **kwargs) # a new figure/axis has to be explicitly added; figsize in inches BUT degrades only
    
    
    def gallery(self, imgs= []):
        """ takes a list (!) of one or more elements and splits it up into 2x2 max. """
        if np.size(imgs)==0:
            print("dude, no images in this folder! {}".format(self.getpath()))
        elif not self.printimg:
            print("withholding images to speed up output process..")
        else:
            while(np.size(imgs)>0): # iterate till all done
                if np.size(imgs)>4:
                    self.picshow_manual(imgs[:4], ncols=2, nrows=2)#take slice of 4, fetch remainder
                    for _ in range(4):
                        imgs.pop(0) # remove 4
                elif np.size(imgs)>2:
                    self.picshow_manual(imgs, ncols=2, nrows=2)#take remainder
                    imgs=[]
                elif np.size(imgs)>1:
                    self.picshow_manual(imgs, ncols=2)#take 2
                    imgs=[]
                else: # ==1:
                    self.picshow_manual(imgs)#take1
                    imgs=[]
                
                
    def pic(self, img):
        """ show one pic """
        self.gallery(imgs=[img])
                
    
    def picshow_manual(self, imgs=[], engine="cv", *args, **kwargs): # give img list and fig size - get gallery, recommended max. 2x2
        self.picframe(*args, **kwargs)
        self.axs = self.roadkill(self.axs) # remove higher dimensions of nxm array, put all into list
        
        for ax in self.axs:
            ax.axis("off")
            
        self.ax_i=-1 # have onward on beginning end to not overflow last time
        for img in imgs:
            self.ax_onward()
            ax=self.get_ax()
            
            # matplotlib imshow params, if needed
            # https://matplotlib.org/api/_as_gen/matplotlib.pyplot.imshow.html
            if engine=="PIL":
                # pillow library --> MOVED DOWN TO IMPORT SWITCH
                from PIL import Image
                ax.imshow(Image.open(img)) # no rotation, theoretically slower
            elif engine=="cv":
                # python-opencv library - linux:pip install opencv-python --> MOVED DOWN TO IMPORT SWITCH
                # pyright, pylance: ignore import error on module not present
                import cv2 # type: ignore
                ax.imshow(cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2RGB)) # auto-rotation, slower on older machine i think
            else:
                print("programmer you fucked up imshow")
            #imgs.pop(0)
            
            
    def complete_gallery(self):
        """ gallery of current dir (calls listfiles-self.images) """
        self.listfiles()#list and store images in self
        self.gallery(imgs=self.images)
        
        
    def rotate_xticks(self, rotation, long=0, ha="right", autoscale=1,to_int=0):
        """ rotate ticks. also fix visual offset if long
            - rotation (degrees)
            - long (bool): further reformatting?
                - ha: horizontal alignment
                - autoscale: re-scale axis
                - to_int: cast auto-fetched xlabels to int?
                    (alternative: use enginerd_xaxis)

        """
        ax=self.get_ax()
    
        # first, rotate 
        #"empty" but sets rotation (_str of this obj returns "Text(0, 0, '')")
        for tick in ax.get_xticklabels():
            tick.set_rotation(rotation)
        
        # then check if longer
        if long:#longer ones might appear shifted to right - compensate!
            
            xticks=ax.get_xticks()
            if to_int:
                vint = np.vectorize(int)
                xticks = vint(xticks)
            ax.set_xticks(xticks)#works but does ugly autoscaling
            # re-autoscale
            if autoscale: # UNLESS you have an imshow then probably not
                usedxticks=list(xticks.copy())
                usedxticks.pop(0)
                usedxticks.pop(len(usedxticks)-1)
                ax.set_xlim(min(usedxticks),max(usedxticks))
            
            """
            # set ha (horizontal alignment) dependent on tick len - DOES NOT WORK
            #l=max([print(str(xtick) for xtick in list(xticks))]) # get generator - wtf!?
            #l=max([len(str(xtick) for xtick in list(xticks.ticks))]) # get longest schlong - no worky
            l=0
            for xtick in list(xticks):
                print(xtick)#wtf - 0.6000000000000001 - how to catch one of these
                l=max(l,len(str(xtick)))
            print(l)
            if l<5:
                ha="left"
            else:
                ha="right"
            """
            
            fontdict={'horizontalalignment':ha}#put in here to pass along
            ax.set_xticklabels(xticks,fontdict=fontdict)#Warning mandatory Axes.set_xticks beforehand!. 
                                                            #Otherwise, the labels may end up in unexpected positions. (mpl >3.3.0, web-doc 3.4.1)
            


    def subplots_adjust(self, *args, **kwargs):
        """ fiddle with the parameters, for spacing
        - left right top bot
        - hspace wspace
        """
        self.get_fig().subplots_adjust(*args, **kwargs)   
        
        
    def hide_frame(self,ax=None):
        """ blank out frame aka hide_frame"""
        self.get_fig().patch.set_visible(False)
        self.get_ax(ax).axis('off')

    def blank(self,ax=None):
        """ blank out frame aka hide_frame"""
        self.hide_frame(ax=ax)
        
    def xlabel(self, label="", **kwargs):
        self.get_ax().set_xlabel(label, **kwargs)

    def ylabel(self, label=""):
        self.get_ax().set_ylabel(label)

    def sudo_xlabels(self, labels=[], x=""):
        ax = self.get_ax()
        if not x:
            x = np.arange(0,len(labels))
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        
    def common_ax_labels(self,xlabel="",ylabel=""):
        """ add a big axis, hide frame """
        fig = self.get_fig()
        fig.add_subplot(111, frameon=False)
        # hide tick and tick label of the big axis
        plt.tick_params(labelcolor='none', which='both', top=False, bottom=False, left=False, right=False)
        plt.xlabel(xlabel)#("common X")
        plt.ylabel(ylabel)#("common Y")


    def nicergrid(self,y_major=20E6, y_minor=2.5E6, x_major=0.5, x_minor=0.1, grid=True, **kwargs):
        """ add x,y grid based on spacings
            - x_minor
            - y_minor
            - x_major
            - y_major
            - kwargs for enginerd_axis x,y
            - grid: on/off (True default)
        
        """
        ax = self.get_ax()

        #axis y         #we have: 20M on left and 2.5*20=50M on right
        ax.yaxis.set_major_locator(MultipleLocator(y_major))
        ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
        ax.yaxis.set_minor_locator(MultipleLocator(y_minor))
        self.enginerd_yaxis(**kwargs)
        #axis x         # 0.1 minor and 0.5 major
        ax.xaxis.set_major_locator(MultipleLocator(x_major))
        ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
        ax.xaxis.set_minor_locator(MultipleLocator(x_minor))
        self.enginerd_xaxis(**kwargs)
        if grid:
            #ax.grid("on")
            # kw b=True got renamed to visible=True, since mpl3.7 depreciated
            ax.grid(visible=True, which='major', color='grey', linestyle='-', alpha=0.5)
            ax.grid(visible=True, which='minor', color='grey', linestyle=':', alpha=0.5)


    def hidey(self):
        """ hide current ax' y-axis label and tick-labels """
        #self.get_ax().yaxis.set_visible(False) # hide ylabels and grid
        self.get_ax().set_yticklabels([]) # hide only values
        #self.get_ax().grid(True)
        self.get_ax().set_ylabel("") # and unit label
        self.get_ax().yaxis.set_major_locator(plt.NullLocator()) # hide ticks "sticks"

    def hidex(self):
        """ hide current ax' x-axis label and tick-labels"""
        #self.get_ax().xaxis.set_visible(False) # hide xlabels and grid
        self.get_ax().set_xticklabels([]) # hide only values
        #self.get_ax().grid(True)
        self.get_ax().set_xlabel("") # and unit label
        self.get_ax().xaxis.set_major_locator(plt.NullLocator()) # hide ticks "sticks"

    def hidexy(self):
        """ hide current ax' xy-axis labels and tick-labels"""
        self.hidex()
        self.hidey()


    ## forwarders ##
    def hist(self, *args, **kwargs):
        """ forward to mpl hist
            x .. input data

            NOTE: whenever possible, use roadkill() to include matrix as list and reduce drawing overhead!!
            for row/col ID and switch, see hist_tester()

            options:
            - percent option
            - auto-range issues!!
                - # example w manual range bins and width
                - xmin=0
                - xmax=300
                - bins=50
                - bin_w = (xmax-xmin)/bins
                - self.hist(x=x, bins = bins, percent=percent, width=bin_w); 
        
        # return n, bins, patches
        
        note: old patchy-draw stuff at bottom of myink as comment
        """

        # extract percent
        if "percent" in kwargs:
            percent = kwargs["percent"]
        else:
            percent = False

        # process args, delete non-hist kwargs
        kwargs = ml.histo_weighter(**kwargs)

        # call plot hist, forward kwargs
        ret = self.get_ax().hist(*args,**kwargs)

        # format
        if percent:
            self.get_ax().yaxis.set_major_formatter(PercentFormatter(1))

        # return n, bins, patches
        return ret


    def imread(self, *args, **kwargs):
        """ route through plt.imread"""
        return plt.imread(*args, **kwargs)

    def text(self, *args, **kwargs):
        return plt.text(*args, **kwargs)

    def rect(self, *args, **kwargs):
        """ draw a rectangle using Patches-Rectangle """
        # (x-start y-start) , width, height
        # eg. (50,100),40,80, edgecolor='red', facecolor='none', lw=4)
        self.get_ax().add_patch(Rectangle(*args, **kwargs))

    def imshowpro(self, mx=None, x_axis=None, y_axis=None, y_label_inverted=False, pixelscale=1, kwargs_fig={}, **kwargs):
        """ souped-up mpl imshow api"""

        # # import conditioning # #
        # data matrix
        if not np.any(mx):
            raise Exception("imshowpro mx: required")
        elif len(np.shape(mx)) >2:
            raise Exception(f"imshowpro mx: too many dims ({len(np.shape(mx))=}, {np.shape(mx)=})")

        # rows then columns
        ydatalen = mx.shape[0]
        xdatalen = mx.shape[1]

        # default init
        xfig = None
    

        # # imshow "extent" doc
        #   - needed to set ticks and grid correctly (not shifted into centers)
        #   - can also label
        #   - (0,0) is upper left of imshow but extent is flipped on y IF y_label_inverted via waterfall
        #   - extent = (0+m, xdatalen+m, ydatalen+n, 0+n)# n,m freely chosen
        #   - print(extent)# with testdata: 0 1001 3 0
        
        # # minima maxima
        # babysitted versions - not needed atm
        #mymin = ml.nanmin
        #mymax = ml.nanmax
        # not babysitted - possible warning spam in stdout
        mymin = np.nanmin
        mymax = np.nanmax

        # check before switch
        if ml.my_any(x_axis):
            if np.average(x_axis) == x_axis[0]:
                self.log.warning(f"identical x_axis values in imshowpro - ignoring array of ({x_axis[0]=})..")
                x_axis = []

        # switch x y axes present
        if ml.my_any(x_axis):
            # setting the extent -- axes' xticks xticklabels
            if ml.my_any(y_axis):
                # app-specific auto-subsample example, add as route-through via inheritence and super()
                # subsample y_axis from 151 to 16 if needed, overwrite orig arg
                #if len(y_axis)>17 and (ydatalen==16):
                #    y_axis=y_axis[0::10]

                if ((np.size(y_axis)) == ydatalen):
                    # inverted for waterfall
                    extent = (mymin(x_axis), mymax(x_axis),mymin(y_axis), mymax(y_axis))
                else:
                    extent = (mymin(x_axis), mymax(x_axis), 0, ydatalen)
                    print(f"FORBIDDEN y_axis extent forbidden in imshowpro, {mx.shape=} vs {y_axis.shape=}")
            else:
                # no y_axis given
                extent = (mymin(x_axis), mymax(x_axis), 0, ydatalen)
        else:
            # no x axis give
            extent = [0,ydatalen,0,xdatalen]
        
        if "aspect" not in kwargs:
            kwargs["aspect"] = "auto" # aspect makes it rect etc #aspect auto enables arbitrary axis limits
        else:
            # determine pixelscale auto or manual mode
            square_operation = kwargs["aspect"] == "square"
            square_cal = kwargs["aspect"] == "square_cal"

            if square_operation or square_cal:
                if "figsize" in kwargs_fig:
                    raise Exception("figsize in square mode not settable\nI'm afraid Dave, I cannot let you do that.")
                else:
                    # aspect ratio dependent on data size,
                    aspect = xdatalen / ydatalen

                    # correct for different x or y axis scaling
                    aspect = aspect * ((extent[1]-extent[0])/(extent[3]-extent[2]))
                    aspect = abs(aspect)
                    #print(aspect)
                    
                    kwargs["aspect"] = aspect

                    # scale factor for pixels
                    #   derived from fontsize 22
                    #   division over 72: pt to inch
                    #   scaled arbitrarily


                    # ydatalen == xdatalen probably
                    max_xlabellen = 0
                    max_ylabellen = 0
                    if max_xlabellen in kwargs_fig:
                        max_xlabellen = kwargs_fig["max_xlabellen"]
                    if max_ylabellen in kwargs_fig:
                        max_ylabellen = kwargs_fig["max_ylabellen"]

                    # some legacy guess
                    if (not max_xlabellen) or (not max_ylabellen):
                        max_xlabellen = 15

                    max_chars = max(max_xlabellen, max_ylabellen)

                    pixelscale_old = pixelscale

                    # # lookuptable instead
                    if not square_cal:
                        if aspect != 1:
                            raise Exception("aspect not implemented in lookuptable - also not useful - how did it happen?")
                        
                        # fetch table
                        df = cplm.get_cal()
                        
                        # case labels are ascending ints
                        if max_chars <= 2:
                            row = df[ ((df["labellen"] == 2) & (df["datalen"] == ydatalen)) ]
                        # case labels are text of length about 20 - there is only that entry atm - HACK
                        else:
                            # exclude maxchars == 2  case with ">2"
                            row = df[ ((df["labellen"] > 2) & (df["datalen"] == ydatalen)) ]
                        
                        #print(row)
                        if len(row)!=1:
                            raise Exception(f"not exactly one match but {len(row)} for {max_chars=}{ydatalen=} in lookuptable: {row}")
                        else:
                            pixelscale = float(row["pixelscale"])
                        
                        #print(max_chars)

                    # # # pixelscale working point, to have input 0.5..1.5
                    # fix size at x=3 but decrease slope, aka add
                    #slopecorr = 0.05
                    
                    #pixelscale *= (-0.1 -slopecorr)*xdatalen + 2 +slopecorr*3
                    #print(f"{pixelscale=}")
                    # calc scaling factor to font
                    fa = 22 / 72 * pixelscale 

                    # calc figsize
                    xfig = xdatalen * fa * (1+ max_chars/100)
                    #xfig = xfig + stripewidth
                    yfig = ydatalen * fa

                    if xfig <0 or yfig<0:
                        raise Exception(f"{xfig=}, {yfig=} at {xdatalen=} with {pixelscale=}, {pixelscale_old=} and {max_chars=}")
                    
            else: #not square
                pass # keep figure, subplot if open, or whatever nothing to do

        # in case a figure is requested
        if kwargs_fig:
            # close current open figure, if empty ax
            self.close("emptyax")

            # create a small figure
            #self.subplots(figsize=(xfig,yfig), **kwargs_fig)
            #self.spinds(cols_def=[1,3], rows_def=[3,1], **kwargs_fig) # spinds dont have big corner
            #self.ecke(type="ru", hidesmallframes=True, figsize=(xfig,yfig)) # HACK ignore kwargs for now
            # HACK - stripewidth mod alone doesnt work, figure needs to be larger
            #self.ecke_ru_only(figsize=(xfig,yfig), stripewidth=stripewidth, outerlen=outerlen)
            #self.ax_i = -1

            # # cb fix # # 
            # to fit still when colorbar is there and not be too small
            if xfig:
                xfig = np.max([1.2, xfig]) 
                # add "resting" space below
                nrows=2
                self.subplots(figsize=(xfig,yfig), nrows=nrows)
            else:
                self.subplots()
            self.ax_onward()# go to row 2
            self.blank() # remove axis lines
            self.ax_backtrack()
            self.ax_i = -1 # put into expected location to start w ax_onward() in a loop


        if y_label_inverted:
            # swap list elements
            extent = list(extent)
            extent[2], extent[3] = extent[3], extent[2]

        kwargs["extent"]=extent
        s = self.imshow(mx, **kwargs)
        #self.autoscale_fig() # call after labels? so outside
        return s


    def imshow(self, *args, **kwargs):
        """ basic forward to mpl imshow,
            plotting an image (png, jpg) or mx    ,
            NOT IMSHOWPRO
        """
        
        im = self.get_ax().imshow(*args,**kwargs)
        # remember handle for colorbar-stuff, eg. common_cb_lims
        self.imims.append(im)

        return im


    def plot(self,*args,**kwargs):#thsmith already has a "plot"
        """ forward to mpl plot"""
        return self.get_ax().plot(*args,**kwargs)

    def scatter(self ,*args , weigh=False, wf=10, **kwargs):
        """ forward to mpl scatter
            - extra option: weigh and wf (weighfactor)
        """
        
        if weigh: # multiple occourances cause large dots 
            #https://stackoverflow.com/questions/46700733/how-to-have-scatter-points-become-larger-for-higher-density-using-matplotlib
            from collections import Counter
            x,y = args
            c = Counter(zip(x,y))
            # create a list of the sizes, here multiplied by wf for scale
            s = [wf*c[(xx,yy)] for xx,yy in zip(x,y)]
            kwargs["s"]=s

        return self.get_ax().scatter(*args,**kwargs)


    def errorbar(self,*args,**kwargs):
        """ forward to mpl errorbar"""
        return self.get_ax().errorbar(*args,**kwargs)

    def stem(self, *args, hidestems=False, hidedots=False, markersize = -1, markercolor="", **kwargs):
        """ stem, options to hide lines etc. """

        # call mpl stem
        markers, stemlines, baseline =  self.get_ax().stem(*args,**kwargs)

        ## post process ##
        
        # hide stuff if requested
        # https://stackoverflow.com/questions/60616721/how-to-remove-stemlines-from-a-matplotlib-stem-plot
        if hidestems:
            stemlines.remove() 
            baseline.remove()
        if hidedots:
            markers.remove()

        # change size if requested
        if markersize>-1:
            markers.set_markersize(1)

        if len(markercolor)>0:
            markers.set_color(markercolor)

        # route through results
        return markers, stemlines, baseline


    def autoscale_fig(self, halt_if_failed=False):
        """
        try to fit most text of axis ticks, labels, titles w.o. overlapping
        - usually works, only GUI panel might overlap still
        - alternatively, use subplots.adjust wspace hspace bottom top
        """
        if halt_if_failed:
            # elevate warnings to be errors
            # https://stackoverflow.com/questions/5644836/in-python-how-does-one-catch-warnings-as-if-they-were-exceptions
            import warnings
            warnings.filterwarnings("error")

            # try to fit everything onto plot
            try:
                plt.tight_layout()
            
            # catch any Warning if generated
            # (here - UserWarning https://docs.python.org/3/library/warnings.html)
            except Warning:
                raise Exception("autoscale fig (plt.tight_layout) failed - plot overflows")
            
            # reset warnings to be warnings-only again
            finally:
                warnings.resetwarnings()

        else:
            # might generate ignorable warning
            plt.tight_layout()


    # https://matplotlib.org/stable/gallery/lines_bars_and_markers/bar_stacked.html
    def barstacked(self, datadict={}, xlabels=[], barwidth=0.5, colorwheel=None, **kwargs):
        """ generate stacked bars, so no datapoints hide each other
            - colorwheel such as gradientplot()"""
        ax = self.get_ax()
        #bottom = np.zeros(len(weight_counts.values()[0])) # how long is one dataset
        bottom = np.zeros(len(xlabels)) # how long is one dataset
        for i, (rowlabel, datarow) in enumerate(datadict.items()):
            if colorwheel:
                kwargs["color"]=colorwheel(i)
            ax.bar(xlabels, datarow, barwidth, label=rowlabel, bottom=bottom, **kwargs)
            bottom += datarow


    def stickplot(self, data, xlabels="", meanoffset=False, ylabel="", title=""):
        """
        boxplot-similar stickplot but mean, stdev, extrema are plotted only

        forked from https://stackoverflow.com/questions/33328774/box-plot-with-min-max-average-and-standard-deviation
        """

        # # data conditioning # # 
        data = np.array(data, dtype=object) # can be a ragged list instead of mxn matrix - suppress the warning
        statistics = []
        for item in data:
            item = np.array(item).astype(np.float64)
            # babysitted numpy nan* evals
            mins = ml.nanmin(item)
            maxes = ml.nanmax(item)
            means = ml.nanmean(item)
            std = np.std(item)
            statistics.append([mins, means, maxes, std])

        mins, means, maxes, std  = np.array(statistics).astype(np.float64).T # unpack
        x=np.arange(len(data))

        if meanoffset:
            off=means
            ylabel+=", means subtracted"
        else:
            off=0

        # # plotting # #
        # create stacked errorbars
        self.errorbar(x, means-off, std, fmt='ok', lw=3) # fat std
        self.errorbar(x ,means-off, [means - mins, maxes - means], fmt='.k', ecolor='gray', lw=1) # thin min-max

        # xy_labelling
        ax = self.get_ax()
        ax.set_ylabel(ylabel)
        ax.set_xticks(np.arange(len(xlabels)))
        ax.set_xticklabels(xlabels, ha="right")#horizontal alignment
        self.rotate_xticks(45, autoscale=0)
        ax.locator_params(axis='x', nbins=10)#, tight=True)
        self.get_ax().minorticks_on()


        self.title(title)
        self.autoscale_fig()


    def boxplot(self, data=[], xlabels="", meanoffset=False, ylabel="", title="", mc = "green",
                availability=False, nan_bad=True, annot=True, **kwargs):
        """
        boxplot

        copied from stickplot, adapted
        - data: input array/list
        - mc: markercolors for mean, std edges upper+lower
        - xlabels: data labels
        - ylabel
        - meanoffset
        - annot: annotate ,ean, mean+-stdev?
        
        availability related:
        - availability: add availability [%] into xlabel?
        - nan_bad: NANs are bad?
            - True: missing datapoints (DEFAULT)
            - False: empty matrix elements (less to count, e.g. padding in some position_matrix)

        # Troubleshooting #
        - data = ml.singledim_mod(data)
            - only keeps first dimension
            - ax.boxplot() dies otherwise sometimes
            - applied all the time, might result in a numpy-nanmean-nonzero error however

        """

        # data conditioning #
        data = np.array(data, dtype=object) # can be a ragged list instead of mxn matrix
        
        # prep collector
        statistics = []

        # loop over data
        for i,item in enumerate(data):
            
            # fustratingly, roadkill w. hard=2 doesn't work here :O,
            # before calling boxplot:
            # data = [ml.roadkill(ele, hard=1) for ele in data]
            # works :O, sadly not at fct start, before or after np.array


            # squish item dimensions down to statistics
            mins = ml.nanmin(item)
            maxes = ml.nanmax(item)
            means = ml.nanmean(item)
            std = np.std(item)
            statistics.append([mins, means, maxes, std])

            # optional user-offset, per loop-item to be compatible w ragged-lists
            if meanoffset:
                off=means
                ylabel+=", means subtracted"
                data[i] = item-off # change loop base data after analysis

        # unpack
        mins, means, maxes, std  = np.array(statistics).astype("float").T

        # consider boxplots are plotted at x-offset of +1 for some reason:
        x=np.arange(len(data))+1


        data = data.T
        # # plotting # #        
        # flierprops == outlier-marker type
        #   - ","==pixel-marker
        flierprops = dict(marker=',', markerfacecolor='black', markersize=12, linestyle='none')
        ax = self.get_ax()
        ax.boxplot(data, flierprops=flierprops, **kwargs)
        if annot:
            self.scatter(x, means+std, marker="^", c=mc, label="mean+stdev") # triag up
            self.scatter(x, means, marker="s", c=mc, label="mean") # square
            self.scatter(x, means-std, marker="v", c=mc, label="mean-stdev") # triag down

        if availability:
            if not xlabels:
                xlabels=np.zeros(len(data.T))
            for i, datacolumn in enumerate(data.T):
                avail_pc = ml.availability_frac(data=datacolumn, nan_bad=nan_bad)*100
                xlabels[i] = f"{xlabels[i]}\n({avail_pc:.1f}%)"


        # # xy_labelling
        ax.set_ylabel(ylabel)
        if np.any(np.array(xlabels, dtype=object)): # a.any() warning fix, for evaluating bool(list([1,2,3])) or bool(list([0,0,0])), bool(list([[],[],[]])) etc.
            xlabels = list(xlabels)
            xlabels.insert(0,0)#insert dummy at begin        
        ax.set_xticks(np.arange(len(xlabels)))
        ax.set_xticklabels(xlabels, ha="right")#horizontal alignment
        self.rotate_xticks(45, autoscale=0)
        ax.locator_params(axis='x', nbins=10)#, tight=True)
        ax.minorticks_on()
        
        # # legend customization
        self.legend()
        from matplotlib.lines import Line2D
        #https://matplotlib.org/stable/gallery/text_labels_and_annotations/custom_legends.html
        medianlinelegendline = Line2D([0], [0], color='orange', marker="_", lw=1, label='Line')
        quartilelegendline = Line2D([0], [0], color='black', marker="_", lw=1, label='Line')
        h, l = ax.get_legend_handles_labels()
        # insert
        l.insert(0,"quartiles")
        h.insert(0,quartilelegendline)
        l.insert(1,"median")
        h.insert(1,medianlinelegendline)
        # put 
        self.legend(handles=h,labels=l)   

        self.title(title)
        self.autoscale_fig()


    def stickplot_summary(self, data=[], xlabels=None, ylabel=None, title=None):
        """ makes boxplot summaries and scenario overlay from "raw datapoints"
        n-dim:
        - data
        - xlabels
        annotations
        - ylabel
        - title
        """
        # # compute overlay # #
        # generate x-axis for all datapoints
        x = [np.ones(len(datasubset))* data.index(datasubset) for datasubset in data]
        x = np.concatenate(x)
        y = np.concatenate(data)

        # vanilla base
        self.stickplot(data=data, xlabels=xlabels, title=title, ylabel=ylabel)

        # put overlay
        self.scatter(x,y)            


    def plot_corr_mx(self, mx, xlabels=[],ylabels=[], clims=[], lowlim=None, cb_label="", optlabel="", pixelscale=1, **kwargs):
        """
        make subplot correlation matrix with imshow

        - mx (mxn array): input matrix
        - xlabels, ylabels
        - clims (2-ele list): limits of colorbar
        - lowlim (float) - clip away lower limit in colormap
        - optlabel (str): put this label in lower left of (white triag) mx
        """
        #mx=ml.mx_diag_mirror(mx)#if full is desired

        ## plot the thing ##
        #raise Exception("i am really here") ok so its not another fct
        #pe.mycanvassize(bigfig=1) # works but sticks and also changes fontsize
        self.canvas_params(figsize=[15,10])#cm
        self.rc_autoreset = 0 # to not reset temporarily, if already set

        # is aspect square?
        if "aspect" in kwargs:
            square_aspect = (kwargs["aspect"] == "square")
        else:
            square_aspect = False
        
        # if yes, route through fig generation
        if square_aspect:
            kwargs_fig = dict(nrows=2, ncols=1)
        # else do it yourself
        else:
            kwargs_fig = {}
            self.subplots(nrows=2, ncols=1)


        #pe.mycanvassize(deffig=1)
        #pe.canvas_params_reset() NOT HERE IT MESSES UP FONTS ON CURRENT

        #ax=self.get_ax()
        cmap = plt.cm.turbo.copy()
        
        if lowlim:
            # modify colormap
            cmap.set_extremes(bad="w")
            #cmap.set_under(color="w")
            
            # mask values
            mx=np.array(mx)
            mx = np.ma.masked_where(mx < lowlim, mx)
            # print(mse)
        
        if ml.my_any(xlabels) and ml.my_any(ylabels):
            max_xlabellen = np.max([len(str(label)) for label in xlabels])
            max_ylabellen = np.max([len(str(label)) for label in ylabels])
            kwargs_fig = {"max_xlabellen":max_xlabellen, "max_ylabellen":max_ylabellen}
        else:
            # assume something
            max_xlabellen = 2
            max_ylabellen = 2

        # # plot
        #  imshow pixely - don't mush it up with interpolation
        imim = self.imshowpro(mx=mx, interpolation="none", cmap=cmap, kwargs_fig=kwargs_fig, pixelscale=pixelscale, **kwargs)
        
        # show all ticks
        if np.size(xlabels):
            self.xticklabels(xlabels, ha="right") # horizontal alignment
        if np.size(ylabels):
            self.yticklabels(ylabels)
        
        # how many labels is too many to display all and rotate?
        thres = 16
        if (len(xlabels) > thres) or (len(ylabels) > thres):
            n=3
            ax = self.get_ax()

            # major ticks that are multiples of n
            # minor ticks that are multiples of 1.  
            ax.xaxis.set_major_locator(MultipleLocator(n))
            ax.xaxis.set_minor_locator(MultipleLocator(1))
            ax.yaxis.set_major_locator(MultipleLocator(n))
            ax.yaxis.set_minor_locator(MultipleLocator(1))

            self.rotate_xticks(45, ha="center", long=1, autoscale=1, to_int=1)
        else:                
            self.rotate_xticks(45)        
        
        self.colorbar(cb_label)
        if len(clims)==2:
            imim.set_clim(clims[0],clims[1])

        # reset figsize after end
        #self.canvas_params_reset() # still messes up
        self.rc_autoreset = 1 # do it only when next subplots() is called

        # dress it up #
        self.ax_onward()
        #self.hide_frame()
        '''
        self.subplots_adjust(top=0.8,#dirty canvas centering fix - exported gui settings after playaround
            bottom=0.0,
            left=0.0,
            right=0.8,
            hspace=0.0,
            wspace=0.15)
        '''
        if optlabel: # HACK
            self.log.warning(f"erasing optlabel {optlabel} for plot_mse_mx lookup table compatibility ..")
            optlabel = ""
        # optlabel annotation, floating in lower left corner
        self.ax_backtrack()
        n = np.shape(mx)[0] #nxn
        """    
        if ymax > 4: # large mx
            ypos = ymax - 1.5 # more negative = more up
            xpos = 0.5 # farther from left
        else: # small mx
            ypos = ymax - 0.65 # less neg = down
            xpos = -0.45 # closer to left
        """
        ypos = n - (0.12*n+0.29)
        xpos = 0.14*n-0.87

        self.get_ax().text(xpos, ypos, optlabel,
            bbox={'facecolor':'white','alpha':1,'edgecolor':'none','pad':1},
            ha='left', va='center') 
        self.ax_onward()

        # fit everything (plot, cbar, labels) onto figure but error out if it overflows
        self.autoscale_fig(halt_if_failed=True)


    # experienced kwargs error - if **kwargs used AND cmap="turbo_r" -> both are ignored
    def waterfall(self, mx=None, ax=None, title=None, # general
                        x_axis = None, places=2,  # x_axis
                        yticks=[], y_minor_grid=None, # y_axis
                        cb_label="mag (dB)", colorbar=True, # values
                        **kwargs): # mixed formatting, picked out, rest goes to imshow
                        # cmap turbo - https://ai.googleblog.com/2019/08/turbo-improved-rainbow-colormap-for.html
        """ plot a matrix without interpolation, set the yticks and stuff
            imshow of mx, aligning yticks
            input:
                - mx
                - x_axis
                - yticks
            annotations 
                - title   
                - places (self.engineerd xaxis)
                - cb_label (colorbar)
                - colorbar (bool or h/w aspect ratio 20<x<200)
                y_minor_grid: spacing of minor y-ticks, if any
            output:
                - mx (same as input)
            """
        
        ## process arguments ##
        if "cmap" not in kwargs:#if switch exists
            kwargs["cmap"]="turbo_r"
        if "interpolation" not in kwargs: # interpol-none removes blurr
            kwargs["interpolation"]="none"
        if "cb_label" in kwargs:
            cb_label=kwargs["cb_label"]
            #and remove, to not confuse the artist (imshow)
            kwargs.remove("cb_label")
        
        if np.size(mx)<2 or np.size(x_axis)<2:
            raise Exception(f"matrix and x_axis input required!, { np.size(mx)}, {np.size(x_axis)}")

        # square pixels
        square_aspect = False
        if "aspect" in kwargs:
            if kwargs["aspect"] == "square":
                square_aspect = True
        
        # # # plotting # # #
        # legacy axis setting
        ax = self.get_ax(ax)

        # main plot
        self.imshowpro(mx=mx, x_axis=x_axis, y_axis=yticks, y_label_inverted=True, **kwargs)
        
        # grid option
        if y_minor_grid:
            self.get_ax().yaxis.set_minor_locator(MultipleLocator(y_minor_grid))
        
        # colorbar options
        #cb = self.colorbar(cb_label)
        #if not colorbar: # colors wrong even though cmap is in kwargs
        #    cb.remove() # mpl 3.5.1 removes :) but space issue
            #self.autoscale_fig() # usecase twinx(), does not work - colorbar1 space is deleted so it overlaps if 2nd colorbar deleted
        if int(colorbar) > 1:
            cb = self.colorbar(cb_label, aspect=colorbar)
        elif colorbar == 1:
            cb = self.colorbar(cb_label)

        # postprocessing        
        self.title(title)
        if places>0:
            self.enginerd_xaxis(places=places)
        if square_aspect:
            self.rotate_xticks(90)
        else:
            self.rotate_xticks(45)

        # return matrix, for legacy reasons
        return np.matrix(mx) 


    def spind_rechts(self, mainwidth=2, smallaxes=2):
        """ 
        make n axes, first left "main" bigger, others same size
        - mainwidth: biggest axis size
        - smallaxes: ammount of axes total
        (copied and mod from ecke) """
        """        
        # total graph slots, for gridspec basis
        n=mainwidth+smallaxes

        # generate plot, get gridspec
        fig, axs = plt.subplots(ncols=n, nrows=1)
        gs = axs[0].get_gridspec()
        
        # hide and remove the original visible subplot axes
        for ax in axs:
            self.blank(ax) 
            ax.remove()
        
        # gridspec magic - make a big ax and some small ones
        axbig = fig.add_subplot(gs[:mainwidth]) 
        axs = np.array([axbig, *[fig.add_subplot(gs[i+mainwidth]) for i in range(0,smallaxes)]])
        
        # put axs inside self
        self.ax = axbig
        self.axs = axs
        self.ax_i = 0
        """
        mylist=[mainwidth, *list(np.ones(smallaxes, dtype=np.int8))]
        return self.spinds(cols_def=mylist)
    

    def spinds(self,
                cols_def=[1,1,3,1], rows_def=[1], # regular features
                keep_old_ax=False, ncols=None, nrows=None, # experimental
                **subplots_kwargs): # passthrough
        """ 
        make n column axes
        - cols_def: array of widths of columns
            - for each column, hava an element
            - the element defines its width
        - rows_def: analog to cols_def with heights
        - keep_old_ax: keep underlying ax, as (auto-)defined by
            - ncols
            - nrows
        """
        
        # total graph slots, for gridspec basis
        #   - auto-def makes evenly spaced subplot axs "grid"
        #   - man-def would allow maybe backdrop-ax w overlay-spinds
        if not ncols:
            ncols = sum(cols_def)
        if not nrows:
            nrows = sum(rows_def)
        
        # generate plot, get gridspec
        fig, axs_mx = plt.subplots(ncols=ncols, nrows=nrows, **subplots_kwargs)
        
        # enable loop also for single line
        if nrows==1:
            axs_mx = [axs_mx] 
        if ncols==1:
            axs_mx = [axs_mx] 
            
        
        # prep collectors
        axold = []
        ax_out = []

        # gridspec magic - fetch main pointer
        gs = axs_mx[0][0].get_gridspec()
        
        # on top left of figure is 0,0
        top = 0 # first height-loop offset
        for height in rows_def:
            # calc edges along z-axis
            bot = top + height
            
            start = 0 # first width-loop offset
            for width in cols_def:
                # calc edges along x-axis
                end = start + width
                # remember new ax; gridspec format: [row-slice,column-slice]
                ax_out.append(fig.add_subplot(gs[top:bot,start:end]))
                start = end # set next width-loop offset
        
            top = bot # set next loop start

        # after gridspec magic, remove or keep old axs
        for axs_row in axs_mx:    
            for ax in axs_row:
                self.blank(ax) 
                if not keep_old_ax:
                    ax.remove()
                else:
                    axold.append(ax)
            
        # put into np.array as expected via other fct
        ax_out = np.concatenate([ax_out,axold])

        # put axs inside self
        self.ax = ax_out[0]
        self.axs = ax_out
        self.ax_i = 0
    

    def spinds_fail(self, mylist=[1,1,3,1], nrows=1):
        """ 
        make n column axes
        - mylist: array of widths of columns
            - for each column, hava an element
            - the element defines its width
        (copied and mod from ecke) """
        
        # total graph slots, for gridspec basis
        n=sum(mylist)
        
        ax_out = []
        fig = plt.figure()
        [print((f"{nrows}{(n-ele)}{i+1}")) for i,ele in enumerate(mylist)]
        [ax_out.append(fig.add_subplot(int(f"{nrows}{(n-ele)}{i+1}"))) for i,ele in enumerate(mylist)]
        
        self.ax = ax_out[0]
        self.axs = np.array(ax_out)
        self.ax_i = 0


    def ecke_ll(self, hidesmallframes=False, **kwargs):
        """
        make a subplot with a big corner in left bot, 5 plots around
        
        (this is not a docstring, look at table layout in code)
        ----------------
        |    |    |    |
        ----------------
        |         |    |
        |         |----|
        |         |    |
        ----------------

        ! loops for population have to start with self.ax_onward() !
        (ax_i set to -1, cannot plot first plot at -1)
        """
        fig, axs = plt.subplots(ncols=3, nrows=3)
        gs = axs[1, 2].get_gridspec()
        
        # remove the underlying axes
        for axsi in axs[1:, :2]: # format [row-slice,column-slice]
            for ax in axsi:
                ax.remove()

        # generate big one
        axbig = fig.add_subplot(gs[1:, :2]) # format [row-slice,column-slice]
        
        if hidesmallframes:
            for axsi in axs:
                for ax in axsi:
                    self.blank(ax)

        fig.tight_layout() # ensure square subplots

        # put axs inside
        self.ax = axbig
        self.axs = axs

        self.axs = np.delete(self.axs, [3,4,6,7])

        self.ecke_axs = axs
        self.ax_i = -1 # dirty solution to have plotting-loop start w. self.onward() and get 0 in first iteration


    def ecke_ru(self, hidesmallframes=False, **kwargs):
        """
        make a subplot with a big corner in right upper corner, 5 plots around
        
        (this is not a docstring, look at table layout in code)
        ----------------
        |    |         |
        |----|         |
        |    |         |
        ----------------
        |    |    |    |
        ----------------

        ! loops for population have to start with self.ax_onward() !
        (ax_i set to -1, cannot plot first plot at -1)
        """
        fig, axs = plt.subplots(ncols=3, nrows=3, **kwargs)
        gs = axs[1, 2].get_gridspec()
        
        # remove the underlying axes
        for axsi in axs[:2, 1:]: # format [row-slice,column-slice]
            for ax in axsi:
                ax.remove()

        # generate big one
        axbig = fig.add_subplot(gs[:2, 1:]) # format [row-slice,column-slice]
        
        if hidesmallframes:
            for axsi in axs:
                for ax in axsi:
                    self.blank(ax)

        fig.tight_layout() # ensure square subplots

        # put axs inside
        self.ax = axbig
        self.axs = axs

        self.axs = np.delete(self.axs, [1,2,4,5])

        self.ecke_axs = axs
        self.ax_i = -1 # dirty solution to have plotting-loop start w. self.onward() and get 0 in first iteration


    def ecke_ru_only(self, outerlen=3, stripewidth=1, hidesmallframes=True, **kwargs):
        """
        make a subplot with a big corner in right upper corner, no plots around only space
        
        options: (count of virtual plots, not px)
        - outerlen: how large is figuresize in total 
        - stripewidth: how large is stripe in relation to bigplot
        
        (this is not a docstring, look at table layout in code)
        ----------------
        |    |         |
        |----|         |
        |    |         |
        ----------------
        |    |    |    |
        ----------------

        ! loops for population have to start with self.ax_onward() !
        (ax_i set to -1, cannot plot first plot at -1)
        """
        fig, axs = plt.subplots(ncols=outerlen, nrows=outerlen, **kwargs)
        gs = axs[1, 2].get_gridspec()
        
        # remove the underlying axes
        for axsi in axs[:outerlen-stripewidth, stripewidth:]: # format [row-slice,column-slice]
            for ax in axsi:
                ax.remove()

        # generate big one
        axbig = fig.add_subplot(gs[:outerlen-stripewidth, stripewidth:]) # format [row-slice,column-slice]
        
        if hidesmallframes:
            for axsi in axs:
                for ax in axsi:
                    self.blank(ax)

        fig.tight_layout() # ensure square subplots

        # put axs inside
        self.ax = axbig
        self.axs = [self.ax]

        self.ecke_axs = axs
        # remove for single-use
        #self.ax_i = -1 # dirty solution to have plotting-loop start w. self.onward() and get 0 in first iteration


    def ecke(self, type="ll", **kwargs):
        """
        make a subplot with a big corner plot (based on mpl gridspec doc official)

        
        (this is not a docstring, look at table layout in code)

        types:
            
            - ll
            ----------------
            |    |    |    |
            ----------------
            |         |    |
            |         |----|
            |         |    |
            ----------------

            - ru
            ----------------
            |    |         |
            |----|         |
            |    |         |
            ----------------
            |    |    |    |
            ----------------

        """
        if type=="ll":
            self.ecke_ll(**kwargs)
        elif type=="ru":
            self.ecke_ru(**kwargs)
        else:
            raise Exception(f" ecke {type=} not implemented")
        

# https://stackoverflow.com/questions/17212722/matplotlib-imshow-how-to-animate
    def make_im_gif(self, data, fn='test_anim.gif', fps=1, sec=4):
        """ takes last self.imshow handle and makes a gif
            - data: array of elements to pass to imshow instances
            - fn: filename
            - fps
            - sec
            CAUTION: last im's axis labeling stays!
        """
        im = self.imims[-1] # last imim

        def animate_func(i):
            if i % fps == 0:
                print( '.', end ='' )

            im.set_array(data[i])
            return [im]

        anim = animation.FuncAnimation(
                                    self.fig, 
                                    animate_func, 
                                    frames = sec * fps,
                                    interval = 1000 / fps, # in ms
                                    )

        #anim.save('test_anim.mp4', fps=fps)# ffmpeg knows, pillow not, extra_args=['-vcodec', 'libx264'])
        anim.save(fn, fps=fps)
        print("saved {}".format(fn))

    def colorbar(self, label="", ax=None, **kwargs):
        """ make a colorbar for the last imshow plot
            - label
            - cmap: mandatory colormap
            - aspect
                - set heigth/width fraction of colormap
                - useful aspect ratio 20<x<200
            - ax (optional): to wich ax (or axs-for-all) to attach to
            """
        ax = self.get_ax(ax)

        # forward certian fw_args to set_label
        kwargs2 = {}
        fw_args = ["horizontalalignment"]
        for fw_arg in fw_args:
            if fw_arg in kwargs:
                # put into new dict and delete from old
                kwargs2[fw_arg]=kwargs[fw_arg]
                kwargs.pop(fw_arg)

        if self.imims:
            mappable=self.imims[-1]
        else:
            cmap = kwargs["cmap"]
            mappable = mpl.cm.ScalarMappable(norm=None, cmap=cmap)

        cb=self.get_fig().colorbar(mappable=mappable, ax=ax, **kwargs) # ( ((3.4.2) , 3.5.1 require cb to have correct color with custom cb!?
        cb.set_label(label, **kwargs2)

        return cb

    def cb_remove(self,i=None):
        """ remove one or all colorbars, index i

            NOTE: DOESNT SEEM TO WORK UNLESS common_CB lims called, or sth
                    maybe needs some plt.update() or sth?
        """
        if i == None:
            # remove all colorbars from collected self.imshow handles (e.g. waterfalls)
            for imim in self.imims:
                if imim.colorbar: # if it has one
                    imim.colorbar.remove()
        else:
            # remove specific indexes cb
            imim = self.imims[i]
            imim.colorbar.remove()


    def common_cb_lims(self, data, nan_allowed=True):
        """ 
            - finds common min/max of data
            - iterates over self.imim
            - sets common colorbar limits
            - resets self.imim
        """
        # squash data, in case of different shapes
        #   works always if np.matrix instances are inside data
        #   (not necessarily with np.array tough, e.g. 1D case)
        if ml.is_ragged(data):
            data = self.roadkill(np.array(data, dtype=object), hard=True)
        else:
            data = self.roadkill(np.array(data)) 

        if nan_allowed:
            mymin=ml.nanmin(data)
            mymax=ml.nanmax(data)
        else:
            # works with non-nan, but fucks up colorscale if nans present
            # effectively warning visually that illegal nans are present
            mymin=np.amin(data)
            mymax=np.amax(data)
        
        #print("{},{}".format(mymin,mymax))
        for imim in self.imims:
            imim.set_clim(mymin,mymax)
            #print(imim)
            #self.get_fig().colorbar(imim,ax=self.get_ax())
        self.imims=[]#del imshow refs after rescaling


    def reset_coordsys(self):
        """ reset coord sys to absolute - eg clean up previous plot random spacing
            - e.g. histos have 0,0 on lower left and not 0,0 on upper right per def --> call before and after annotating it w plot 

            NOTE: DANGER - MIGHT KILL x,y ticks
        """ 
        self.get_ax().margins(0) # AFTER plot - 
        self.twinx() # new axes for both
        self.twiny()
        self.hidexy() # hide xy labels etc


    #</myinkc> - if an indent level is wrong fcts afterwards not defined!

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def tester():
    """module test, superseeds ifdef-main (since used here for import shenanigans)"""

    with hoppy.hopper(modulepath):
        if not os.path.exists("myfigures/stinkbug.webp"):
            raise Exception("for selftest of myinkc, please go (cd) to vigilant_tribbles and run \"python myink.py\" there")

        lsq_line_test()
        test_fontsize()
        tickrot()
        stemmy()
        weigh_scatter()
        ecke_tester()
        ecke_tester(type="ru")
        spind_tester()
        test_make_im_gif()
        mycanvassize_test()
        myinkc().mycanvassize(medfig=True) # reset afterwards via one-time-use myinkc element
        test_waterfall()
        histo_test_and_modlegend()
        doublebarrel_barberpole()
        statistics_visu()
        boxplottest()
        #calibrate_corr_mx_label()
        #test_waterfall_size() # not applicable unless calibrated before - HACK: todo (only done for production msr stuff atm)
        myinkc().bug()
        gradientmaster_test()
        test_rect()
        test_spinds_axold()
        test_spinds_axold_inv()


def test_rect():
    pe = myinkc()
    pe.subplots(ncols=2)
    pe.plot([0,100], [0,100])
    
    # (x-start y-start) , width, height
    pe.rect((50,100),40,80,
                    edgecolor='red',
                    facecolor='none',
                    lw=4)
    
    pe.ax_onward()
    pe.plot([0,200], [0,200])
    
    pe.rect((50,100),40,80,
                    edgecolor='red',
                    facecolor='none',
                    lw=4)
    pe.show()


def test_spinds_axold():
    """ go over two spinds and onto third underlying old_ax"""
    pe = myinkc()
    pe.spinds([1,1],keep_old_ax=True)
    colors = ["red","green","blue"]
    
    for i in [1,2,3]:
        pe.blank() # old lower ax can only seen if blank
        pe.plot([0,100], [0,i*100],color=colors[i-1])
        
        # (x-start y-start) , width, height
        pe.rect((50,i*100),40,80,
                        edgecolor=colors[i-1],
                        facecolor='none',
                        lw=4) # note: zorder can't put front-ax (new) below oldax (below)
        pe.ax_onward()
        
    # finally
    pe.show()


def test_spinds_axold_inv():
    """ go over one overlay spind and over two underlying old_ax"""
    pe = myinkc()
    pe.spinds([1],ncols=2, keep_old_ax=True)
    colors = ["red","green","blue"]
    
    for i in [1,2,3]:
        pe.blank() # old lower ax can only seen if blank
        pe.plot([0,100], [0,i*100],color=colors[i-1])
        #pe.text([0,105], [0,i*105],str(i)) # why text nonfunctional; its not pe.blank
        
        # (x-start y-start) , width, height
        pe.rect((50,i*100),40,80,
                        edgecolor=colors[i-1],
                        facecolor='none',
                        lw=4) # note: zorder can't put front-ax (new) below oldax (below)
        if i<3:
            pe.ax_onward()
        
    # finally
    pe.show()


def lsq_line_test():    
    ele = myinkc()
    print(ele.defaultcolorlist())
    
    x = np.array([0, 1, 2, 5])
    y = np.array([-1, 0.2, 0.9, 2.1])
    
    k, d = ele.LSQ_line(x,y)
    
    #ele.subplots()
    #ele.plot_mag()#this is in thvsia
    plt.plot(x, y, 'o', label='Original data', markersize=10)
    plt.plot(x, k*x + d, 'r', label='Fitted line', c=ele.defaultcolorlist()[1])
    plt.legend()
    plt.show()
    
    #ele.modlegend("hellO") # take some ax function to test ax property


def test_fontsize():
    large_title2()
    large_alltext()


def large_title2():
    with myinkc() as ele:
        #plt.subplots(nrows=2)
        ele.subplots(nrows=2)
        ele.title("regular size title")
        ele.ax_onward()
        ele.rcparams_update({'font.size': fontsizes["bigfig"]})
        ele.title("biig title")
        ele.show()
        # with-context doesnt clear that, so manually reset        
        ele.rcparams_update({'font.size': fontsizes["deffig"]})


def large_alltext():
    large_title2()


def histo_test_and_modlegend():
    """ test the hist fct adaptions - percent, matrix input, and modlegend """
    ele = myinkc()
    #ele.rcparams_update({'font.size': 22})
    
    # first set is a quartett #
    ele.subplots(nrows=2, ncols=2)
    ele.suptitle("histo comparision")

    for percent in [False, True]:
        ele.title(f"one element 2 times, percent:{percent}")
        ele.hist(x=[1.0,1.0], percent=percent)
        ele.ax_onward()
        
        ele.title(f"3 elements 3 times, percent:{percent}")
        ele.hist(x=[1,2,3,1,2,3,1,2,3], percent=percent)
        if percent==0:
            ele.ax_onward()
    ## fix label clipping ##
    ele.autoscale_fig()
    
    # second send is a mx example #
    ## data ##
    x = np.array([[1,1], [1,2], [0,0]])
    rows = ["ones", "mixed", "zeros"]
    cols = ["col A", "col B"]
    ele.subplots()
    ele.imshow(x)

    ## plot def ##
    def myhist(x, names):
        ele.subplots(ncols=2)
        ele.hist(x=x, percent=True)
        ele.modlegend(names)
        ele.ax_onward()
        #kwargs =dict(percent=True, histtype = 'bar' , stacked = True )
        ele.hist(x=x, percent=True, histtype = 'bar' , stacked = True )
        
        ele.modlegend(names)
        ele.suptitle("bargraph - notstacked vs stacked")

    # plot
    myhist(x=x, names=cols)
    myhist(x=x.T, names=rows)

    # show all #
    ele.show()


def tickrot():
    # testdata and root obj
    x1=np.arange(1,20)
    x2=np.arange(1,20000)
    ele=myinkc()

    # regular graph
    ele.subplots(nrows=2)
    plt.plot(x1,x1)
    ele.ax_onward()
    plt.plot(x2,x2)
    ele.suptitle("normal labels")
    ele.show()

    # modified graphs
    ele.subplots(nrows=2)
    plt.plot(x1,x1)
    ele.rotate_xticks(rotation=45)
    ele.ax_onward()
    plt.plot(x2,x2)
    
    ele.rotate_xticks(rotation=45,long=1)
    ele.suptitle("rot labels")
    ele.show()


def stemmy():
    stuff=np.random.random(size=10)

    ele=myinkc()
    ele.stem(stuff, hidestems=True)
    ele.title("no stemlines")
    ele.show()

    ele.stem(stuff)
    ele.title("stemlines normal")
    ele.show()


def weigh_scatter():
    ele=myinkc()
    x=[0,1,1,2,2,2,2,2]
    y=[0,1,2,3,3,3,3,5]

    ele.scatter(x,y,weigh=True)

    ele.show()


def ecke_tester(type="ll"):

    # basic
    ele=myinkc()
    ele.ecke(type=type)
    ele.scatter([1,2,3,4],[1,2,1,0])

    for i in range(0,5):
        ele.ax_onward()
        ele.scatter(i,i)

    # images
    ele=myinkc()
    ele.ecke(hidesmallframes=True, type=type)
    ele.scatter([1,2,3,4],[1,2,1,0])

    pics = get_pics()
    for i in range(0,5):
        ele.ax_onward()
        ele.imshow(pics[i])
        #ele.blank() # hide axes, etc around images

    # todo - arrows pointing
    # https://stackoverflow.com/questions/44060063/connectionpatch-or-pyplot-arrow-between-subplots-of-pyplot-pie-charts
    # or annotate each one w emoji and assign this way
    # https://i.stack.imgur.com/Za66N.png

    # finally, show
    ele.show()


def ecke_tester_ru_only():
    ele=myinkc()
    
    ele.ecke_ru_only(outerlen=4, stripewidth=1)
    ele.ecke_ru_only(outerlen=4, stripewidth=2)
    
    ele.show()


def spind_tester():
    ele=myinkc()

    ele.spind_rechts(mainwidth=2,smallaxes=2)
    ele.suptitle("layout: big and 2 small ones")
    
    ele.spind_rechts(mainwidth=4,smallaxes=3)
    ele.suptitle("layout: huge and 3 small ones")
    
    cols_def = [1,1,3,1]
    rows_def = [1]
    ele.spinds(cols_def=cols_def, rows_def=rows_def)
    ele.suptitle(f"layout: {cols_def}, {rows_def=}")
    
    rows_def = [1,1]
    cols_def=[1,2,1]
    ele.spinds(cols_def=cols_def, rows_def=rows_def)
    ele.suptitle(f"layout: {cols_def}, {rows_def=}")
    for i in range(0,6):
        ele.scatter([1,2],[1,2])
        if i<5:
            ele.ax_onward()

    ele.show()


def legend_scrollbar_test():
    ele=myinkc()
    
    #https://stackoverflow.com/questions/55863590/adding-scroll-button-to-matlibplot-axes-legend
    n = 50
    t = np.linspace(0,20,51)
    data = np.cumsum(np.random.randn(51,n), axis=0)

    ele.subplots()

    for i in range(data.shape[1]):
        ele.plot(t, data[:,i], label=f"Label {i}")


    ele.legend(loc="upper left", bbox_to_anchor=(1.02, 0, 0.07, 1))

    ele.make_legend_scrollbar()
    ele.show()


def get_pics():
    """ get some demo pics"""
    from PIL import Image
    pics = []

    # using PIL
    pics.append(Image.open("myfigures/stinkbug.webp")) # plt / PIL demo pic
    pics.append(Image.open("myfigures/stinkbug.webp")) # plt / PIL demo pic
    #pics.append(Image.open("myfigures/pic.png")) # rm ugly mspaint demopic

    # import matplotlib.image as mpimg
    import matplotlib.cbook as cbook
    sample_data = ['grace_hopper.jpg',"logo2.png", "Minduka_Present_Blue_Pack.png"]

    # or mpl
    for sample in sample_data:
        with cbook.get_sample_data(sample) as image_file:
            pics.append(plt.imread(image_file))

    return pics


def mycanvassize_test():
        ele=myinkc()
        
        for key in figsizes.keys():
            kwargs = {}
            kwargs[key]="True"
            ele.mycanvassize(**kwargs)
            ele.subplots()
            ele.plot()
            ele.title(key)
        
        ele.show()


def test_make_im_gif():
    ele=myinkc()
    sec = 4
    fps = 1
    data = [ np.random.rand(5,5) for _ in range( 4 * 1 ) ]

    # First set up the figure, the axis, and the plot element we want to animate
    #fig = plt.figure( figsize=(8,8) )
    ele.subplots()

    a = data[0]
    im = ele.imshow(a, interpolation='none', aspect='auto', vmin=0, vmax=1)

    ele.make_im_gif(data=data)


def test_waterfall():
    # generate test data
    data = np.random.rand(5,5)
    x_axis = np.arange(1E6, 5E6, 1E6)
    print(f"{x_axis=}, {np.shape(x_axis)=}, {np.shape(data)=}")

    # plot
    ele=myinkc()
    ele.subplots()
    ele.waterfall(mx=data, title="random waterfall", x_axis=x_axis, cb_label="colorbar_label")
    ele.show()


    # generate test data
    data = np.diag([1,2,3,4,5])
    x_axis = np.arange(1E6, 5E6, 1E6)
    print(f"{x_axis=}, {np.shape(x_axis)=}, {np.shape(data)=}")

    # plot
    ele=myinkc()
    ele.subplots()
    ele.waterfall(mx=data, title="ascending waterfall", x_axis=x_axis, cb_label="colorbar_label")
    ele.show()


def test_waterfall_size():
    # generate test data
    data = np.random.rand(5,5)
    x_axis = np.arange(1E6, 5E6, 1E6)
    print(f"{x_axis=}, {np.shape(x_axis)=}, {np.shape(data)=}")

    alpha = 0.85

    # plot
    ele=myinkc()
    ele.waterfall(mx=data, title=f"random waterfall, smaller, {alpha=}", x_axis=x_axis, cb_label="colorbar_label", aspect="square", alpha=alpha)
    ele.show()


def doublebarrel_barberpole():
    pe = myinkc()
    pe.subplots(ncols=2)

    x = [0,1,2,3]
    y = [-15,0,5,18]


    xlabel = "xlabel (unit)"
    l1 = ""
    l2 = ""
    g_ylabeltext = "ylabel (unit)"

    pe.yticklabels("") # clear yticks from left graphs y-axis
    #pe.rotate_xticks(45) # somehow this needs massaging and waterfall's rotate doesn't count on twinx
    pe.subplots_adjust(wspace=0.3)

    pe.ylabel(g_ylabeltext)

    pe.xlabel(xlabel) # before twinx!!
    pe.twinx() # new axis to put label right # x is true, makes another y-axis as its dual-x
    # graph 1
    pe.plot(x, y)
    pe.axlabel(l1)

    pe.title("")
    #pe.yticklabels("") # clear yticks from left graphs new y-axis # REMOVE IN PEEKBASE
    # clear only labels not ticks
    pe.get_ax().set_yticklabels("")

    # graph 2 prep
    pe.ax_onward()
    # graph 2
    pe.plot(x, y)

    # get tick array, labels are empty atm as ticks shown directly
    yticks = pe.get_ax().get_yticks()
    # set tick labels instead of ticks directly, format text
    pe.get_ax().set_yticklabels(yticks, ha="center", position=(-0.1, 0))

    # graph 2 post
    pe.axlabel(l2)
    pe.xlabel(xlabel)

    cb_label = " i am text, unittext (unit)"
    pe.colorbar(label=cb_label, cmap="turbo", location="bottom", horizontalalignment="center", ax = pe.axs)# attach to axs aka all_axes not just one sub-ax

    pe.show()


def axis_inversion_test():
    pe = myinkc()

    pe.subplots(nrows=3, ncols=2)
    x=[1,2,3,4,5]
    y=[10,5,1,2,1]
    x=np.array(x)
    y=np.array(y)

    pe.plot(x,y)
    pe.title("x,y")

    pe.ax_onward()
    pe.plot(y,x)
    pe.title("y,x")

    pe.ax_onward()
    pe.plot(y,-x)
    pe.title("y,-x")

    pe.ax_onward()
    pe.plot(y,-x)

    ax=pe.get_ax()
    yticks = ax.get_yticks()
    #ax.set_yticks(np.flip(yticks))
    # are floats, remove unnecessary .0
    vint = np.vectorize(int)
    yticks = vint(yticks)
    # invert
    yticks = -yticks
    ax.set_yticklabels(yticks)
    pe.title("y,-x, relabeled")

    pe.ax_onward()
    pe.plot(y,x)
    pe.title("y,x - ylim and invert_yaxis")
    ax=pe.get_ax()
    ax.set_ylim(ax.get_ylim()[::-1])
    ax.invert_yaxis()


    pe.show()


def tex_test():
    pe = myinkc()
    pe.subplots(nrows=2)

    metrictext = "||A||_F"
    pe.plot()
    pe.title(metrictext)

    pe.ax_onward()
    
    # https://matplotlib.org/stable/tutorials/text/usetex.html
    def frob_texheader():
        dict = {'text.usetex': True, "font.family": "Helvetica"}
        return dict
    pe.rcparams_update(frob_texheader())

    metrictext = r"$ \left \| A \right \|_F $"
    
    pe.plot()
    pe.title(metrictext)

    pe.autoscale_fig()
    
    pe.show()


def narrow_colorbar_test():
    #https://stackoverflow.com/questions/33443334/how-to-decrease-colorbar-width-in-matplotlib
    pe = myinkc()
    pe.subplots()

    x = np.random.normal(0.5, 0.1, 1000)
    y = np.random.normal(0.1, 0.5, 1000)
    
    hist = plt.hist2d(x,y, bins=100)

    cmap = plt.cm.turbo.copy()
    for aspect in [20,100,200]:
        pe.colorbar(cmap=cmap, aspect=aspect)
    
    pe.show()


def statistics_visu():
    y = [1,1,1,1,1,1,1,5,2,2,2,-10, -3, -3, -3]
    x = [1 for i in y]

    pe = myinkc()

    pe.subplots(ncols=2)
    pe.suptitle("raw input data")
    pe.scatter(x,y, color="black")
    pe.title("unweighted scatter")

    pe.ax_onward()
    pe.scatter(x,y,weigh=True)
    pe.title("weighted scatter")

    pe.subplots(ncols=3)
    pe.suptitle("graphing methods")
    pe.boxplot([y])
    pe.title("actual boxplot")

    pe.ax_onward()
    pe.stickplot([y])
    pe.title("stickplot")

    pe.ax_onward()
    pe.get_ax().violinplot(y, showmeans=True, showmedians=True)
    pe.title("violin plot\n+ means meridians ")

    pe.autoscale_fig()

    pe.show()



def boxplottest():
    y = [1,1,1,1,1,1,1,5,2,2,2,-10, -3, -3, -3]

    pe = myinkc()

    pe.subplots()
    pe.boxplot([y,-np.array(y)], xlabels=["y", "-y"])

    pe.show()


def calibrate_corr_mx_label(ns = range(3,10), labellen=1, **kwargs):
    pe = myinkc()
    clims = []
    
    for n in ns:
        #mx = np.random.random(size=(n,n))
        #folderlabels = ["" for i in range(0,n)]
        folderlabels = np.arange(0,n, dtype=np.int8)

        # elongate labels?
        folderlabels = ["".join([str(flabel) for _ in range(0,labellen)]) for flabel in folderlabels]

        vec = np.random.random(size=(n))
        mx = np.diag(vec)
        mx[mx==0] = np.nan
        pe.plot_corr_mx(mx=mx,xlabels=folderlabels, ylabels=folderlabels, clims=clims, optlabel="", cb_label="1E", **kwargs)

        pe.show()


def get_maximum_gui_plot_figsize():
    # usecase: figure looks nice maximized, how to save it automatically? howto extract fig size:
    # https://stackoverflow.com/questions/62195970/get-size-of-maximized-matplotlib-figure
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()

    plt.pause(0.0001)

    fig = plt.gcf()
    print(fig.get_size_inches())


def gradientmaster_test():
    # testdata
    datas = [i+np.arange(0,10) for i in range(0,20)]
    x = np.arange(0,10)
    # g obj
    g = gradientmaster(len(datas))
    # plot ele
    pe = myinkc()
    i=0
    for item in datas: 
        pe.plot(x, item, color=g.cycle(i), label=i)
        i+=1
    pe.legend()
    pe.show()


def barstacked_test():
    pe = myinkc()
    pe.barstacked(datadict={"row0":[2,3], "row1":[1,3], "top": [1,2]}, xlabels=["tower small", "tower big"])
    pe.legend()
    pe.show()


#-#-# module test #-#-#
if testing:#call if selected, after defined, explanation see above
    #tester() # better - call myink_demos.ipynb
    #legend_scrollbar_test()
    #narrow_colorbar_test()
    #spind_tester()
    #gradientmaster_test()
    #barstacked_test()
    
    #test_waterfall()
    #test_waterfall_size()
    
    #calibrate_corr_mx_label(aspect="square", labellen=8, pixelscale=1)
    #calibrate_corr_mx_label(ns = [3], aspect="square_cal", labellen=20, pixelscale=1) # len 20 for 5 datasets is smallest use atm
    #calibrate_corr_mx_label(ns = [3,4,5,6,7], aspect="square", labellen=20, pixelscale=1) # len 20 for 5 datasets is smallest use atm
    #calibrate_corr_mx_label(ns = [40], aspect="square", labellen=1, pixelscale=1) # len 20 for 5 datasets is smallest use atm

    #test_rect()
    #test_spinds_axold()
    test_spinds_axold_inv()
    

    #ecke_tester()
    #ecke_tester(type="ru")
    #ecke_tester_ru_only()

    #histo_test()
    #doublebarrel_barberpole()
    #tex_test()
    #statistics_visu()
    #boxplottest()
    #calibrate_corr_mx_label()
    pass


""" 
plt.hist stuff using bins,patches, copied from metric - unused
#
        #do some gradient magic - todo: check for "right axis" 
        #https://stackoverflow.com/questions/23061657/plot-histogram-with-colors-taken-from-colormap
        
        import matplotlib.pyplot as plt
        #cm = plt.cm.get_cmap('RdYlBu_r')
        cm = plt.cm.get_cmap('turbo_r')
        bin_centers = 0.5 * (bins[:-1] + bins[1:])

        # scale values to interval [0,1]
        col = bin_centers - min(bin_centers)
        col /= max(col)

        # apply
        for c, p in zip(col, patches):
            plt.setp(p, 'facecolor', cm(c))

        draw_colorbar = False # works but manual colorbars mess up last outline plot - $maybe horizontal? below all plots
        if draw_colorbar:
            # make colorbar
            #fig, ax = plt.subplots()
            #fig.colorbar()
            #cb=self.get_fig().colorbar(imim,ax=ax)
            #cb.set_label(cb_label)
            #plt.colorbar() #noo mapper
            
            #https://stackoverflow.com/questions/41661409/how-to-generate-a-colorbar-for-manually-colored-plots-in-matplotlib
            from mpl_toolkits.axes_grid1 import make_axes_locatable 
            import matplotlib as mpl
            divider = make_axes_locatable(plt.gca())
            ax_cb = divider.new_horizontal(size="5%", pad=0.05)    
            cb1 = mpl.colorbar.ColorbarBase(ax_cb, cmap=cm, orientation='vertical')
            plt.gcf().add_axes(ax_cb)
    #</patchy>
"""
