
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 18 21:26:53 2020
@author: thirschbuechler
"""
import re
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import EngFormatter #enginerd stuff
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter) # nicergrid

try:
    import mystring as ms
    #from portal import portal
    import hopper as hoppy
except:
    try:
        import vigilant_tribbles.mystring as ms
        from vigilant_tribbles import hopper as hoppy
        #from vigilant_tribbles.portal import portal

    except:
        print("failed to import module directly or via submodule -  mind adding them with underscores not operators (minuses aka dashes, etc.)")


#from matplotlib.patches import Arc, Circle

#from PIL import Image # pillow library --> MOVED DOWN TO IMPORT SWITCH
#import cv2 # python-opencv library - linux:pip install opencv-python --> MOVED DOWN TO IMPORT SWITCH

#from skimage import idata, icolor
#from skimage.transform import rescale, resize, downscale_local_mean

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


## thing to make matplotlib access easier ###
class myinkc(hoppy.hopper): 
    
    def __init__(self, tikz=False, *args, **kwargs):
        """ init some vars, mostly passing args to superclass """
        # note: matplotlib may need to be reloaded to quit xkcd mode
        # importlib.reload(plt) # not required anymore (using with-context)
        self.ax = None
        self.fig = None
        self.subplot_counter = 0
        self.tikz = 0
        
        self.imims=[] # remember imageshows for rescaling - common_cb_lims

        self.printimg=True # shall images be printed
        self.yright=None # var to be inspected on plot cleanup and reset

        kwargs = self.mycanvassize(**kwargs)
        
        super().__init__(*args, **kwargs) # superclass init, in case there is any

        if tikz:
            self.tikz_enable()


    def mycanvassize(self, **kwargs):
        """ take bigfig/medfig and make it happen!
            - get kwargs
            - adjust canvas/subplots
            - pop used parameters
            - return kwargs without used params
            """
        figsizes = {"bigfig":[15,10], "medfig":[10,6.6], "widefig" : [2*6.4, 4.8], "tallfig" : [6.4, 2*4.8], "dwarffig" : [6.4, 4.8/2]}
        fontsizes = {"bigfig":5, "medfig":4, "widefig":4, "tallfig":4, "dwarffig":3}
        # bigfig for jupyter fullwidth graphs
        #uni_angle = '\U00002222'
        
        for key in figsizes.keys():
            if key in kwargs:
                self.canvas_params(fontsize=fontsizes[key],figsize=figsizes[key])
                kwargs.pop(key)

        return kwargs


    def tikz_enable(self):
        plt.style.use("ggplot")
        self.tikz = 1


    def tikz_save_lastgraph(self, fn="graph"):
        
        # fetch title #
        if fn!="graph":
            title = fn
        elif self.current_suptitle:
            title = self.current_suptitle
        else:
            title = self.current_title
        
        # filename #
        fn = "{}_{}.tex".format(title, self.subplot_counter)
        fn = self.sanitize(fn)
        fn = fn.replace("/", "")# don't get folders by a desanitzed slash-n
        import os
        fn = os.path.join("tikz_out",fn)

        # save #
        import tikzplotlib
        tikzplotlib.save(fn)
        print("tikz saved {} in {}".format(fn, self.getpath() ) )
        #self.subplot_counter+=1 # nope subplots does that
        
        
    def subplots(self, *args, **kwargs):
        """ make subplot axes (plt.subplots(..)) and save axs for iterating via fct
            - ax_onward
            - ax_backtrack
            - ax_move(int) #relative
            """
        # # cleanup last graph  # #
        # save tikz if enabled #
        if self.tikz: # if enabled - save here and with self.show()
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
        """close old plots
        CAVEAT: unless new console for each call (i.e. in vscode)
        """
        plt.close(st)
    
    def show(self):
        """ show last plots - for non-spyder IDEs which need manual trigger """
        if self.tikz: # if enabled
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
        self.rcparams_update({'font.size': 10, 'figure.figsize': [6.4, 4.8], 'figure.dpi': 100})

    def savefig(self,*args, **kwargs):
        plt.savefig(*args, **kwargs)


    def ax_onward(self):
        """ move to next subplot axis """
        self.ax_move(1)
        return self.ax
        
    
    def ax_backtrack(self):
        """ move to prev subplot axis """
        self.ax_move(-1)
        return self.ax
    
    
    def roadkill(self, thing, hard=False):
        """ flatten if possible - remove any dimensions and make a list """
        if (hasattr(thing, "__iter__")):
            if not hard:
                return(thing.flatten()) # please be flat
            else:
                # sudo be_flat
                # - join np.arrays in list via conc
                # - then join lists via ravel)
                return(np.concatenate(thing).ravel())

        else:
            return thing
    
            
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
    
    
    def twinx(self, ax=None, yleft=None, yright=None, yleftadd=None, yrightadd=None):#make right axis #$todo:insert into axs maybe?
        ax = self.get_ax(ax)#save old left
        #self.pacman_worker(ax)#on left
        
        self.ax = ax.twinx()#make right
        self.axdir="r"#next pacman_worker would be right
        
        #todo: make work #sandbox_14
        addmode=(yleftadd!=None and yrightadd!=None)
        writemode=(yleft!=None and yright!=None)
        if addmode or writemode:
            if addmode:    # then add
                ylabell=ax.get_ylabel()#get old ax label
                ylabelr=self.ax.get_ylabel()#get new label
                print(ylabelr)
                print(yleftadd)
                spacer = "  "#two spaces
                
                yleft=ylabell+spacer+yleftadd
                yright=ylabelr+spacer+yrightadd
                self.yright=yright
            
            ax.set_ylabel(yleft)#set left axis
            #self.ax.set_ylabel(yright)#set right axis#do later, after plotting in resetplot          
            
    
    def twiny(self, ax=None):#make top axis
        ax = self.get_ax(ax)
        self.ax = ax.twiny()
    
    
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
        self.enginerd_axis( ax.xaxis, unit=unit, **kwargs)
        

    def enginerd_yaxis(self, ax=None, unit='Hz', **kwargs):
        ax = self.get_ax(ax)
        self.enginerd_axis(ax.yaxis, unit=unit, **kwargs)        
        

    def enginerd(self, value, unit='', **kwargs):#todo: enginerd object/mystring-outsourcing instead of calling it this badly here and axis wise
        """ return engineer-nerd formatted string for a given float
            optional:
            - places : how many decimals (default = 2)
            - unit (str t append)
            - sep: separator (str, default Unicode-thin-space, non-ascii!)
        """
        # load defaults if necessary
        if not "places" in kwargs:
            kwargs["places"]=2 # decimal acc
        if not "sep" in kwargs:
            kwargs["sep"]="\N{THIN SPACE}"
            
        #print(kwargs["places"])
        #if kwargs["places"] > 0: # inactive for -1#does not work here, only in waterfall directly!?!?! #HACK
        return(EngFormatter(**kwargs).format_eng(value)+unit)
    
        
    def enginerd_axis(self, axissub="", unit='Hz', **kwargs):
        # https://matplotlib.org/3.1.0/gallery/text_labels_and_annotations/engineering_formatter.html
        
        if axissub=="":
            axissub=plt.gca().xaxis # as default param, this would create
            #  an empty fig on importing, even without an obj instance
        
        # load defaults if necessary
        if not "places" in kwargs:
            kwargs["places"]=2 # decimal acc
        if not "sep" in kwargs:
            kwargs["sep"]="\N{THIN SPACE}"
        
        # set
        axissub.set_major_formatter(EngFormatter(**kwargs))
    
    
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
        ax = self.get_ax()
        ax.legend(**kwargs)


    def modlegend(self, mylegendtext=None, addtext=None, title=None, rmsubstr=None, ax=None, *args, **kwargs):#, *args, **kwargs for ax.legend only
        """ legend handler and creator 
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
    
    
    def comradelegend(self, fig=None, **kwargs): 
        """ collect all labels of one figure and collate to one master legend 
            locations "loc": 
                - upper/lower left/right/center - equals
                - loc="ul/ll/lr/ur/c"
        """
        fig=self.get_fig(fig)#fetch
        
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

            elif kwargs["loc"]=='c': # center - of figure not current ax :(
                kwargs1=dict(bbox_to_anchor=[0.5, 0.5], loc='center', borderaxespad=0.)
                
            else:
                print("programmer, you screwed up.")
                os.close(0)
            
            # in any case:
            kwargs.update(kwargs1)
        
        # collect old legends
        #https://stackoverflow.com/questions/9834452/how-do-i-make-a-single-legend-for-many-subplots-with-matplotlib
        lines_labels = [ax.get_legend_handles_labels() for ax in fig.axes]
        lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
        # kill old legends
        for ax in fig.axes:
            self.killlegend(ax)
                
        # finally we invoke the legend 
        fig.legend(lines, labels, **kwargs)
        
        
    def comradeaxlegend(self, ax=None, **kwargs):
        """ collect all labels of one axis and collate to one master legend """
        ax = self.get_ax(ax)

        # fuckin' babysit legend placing...
        yoff = 0.12 # empirical 
        xoff = 0.11
        if "outside" in kwargs:
            if kwargs["outside"]:
                yoff = 0 # would place it diagonally outside ON FULLSCREEN FIG ONLY $$todo: get dependent on size? aaa
                xoff = 0
            kwargs.pop("outside") # don't pass downstream matplotlib

        
        if "loc" in kwargs:

            if kwargs["loc"]=='lr':#lowerright
                kwargs1=dict(bbox_to_anchor=(1-xoff, yoff), loc='lower right', borderaxespad=0.)
            
            elif kwargs["loc"]=='ll':#lowerleft
                kwargs1=dict(bbox_to_anchor=(xoff+0.025, yoff), loc='lower left', borderaxespad=0.)
                
            elif kwargs["loc"]=='ul':#upperleft
                kwargs1=dict(bbox_to_anchor=(xoff+0.025, 1-(yoff+0.01)), loc='upper left', borderaxespad=0.)
                
            elif kwargs["loc"]=='ur':#upperright
                kwargs1=dict(bbox_to_anchor=(1-xoff, 1-(yoff+0.01)), loc='upper right', borderaxespad=0.)
                
            else:
                print("programmer, you screwed up.")
                os.close(0)
            
            # in any case:
            kwargs.update(kwargs1)
        
        
        # collect old legends
        #https://stackoverflow.com/questions/9834452/how-do-i-make-a-single-legend-for-many-subplots-with-matplotlib
        lines_labels = ax.get_legend_handles_labels()
        lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
        # kill old legends
        
        self.killlegend(ax)
                
        # finally we invoke the legend (that you probably would like to customize...)
        ax.legend(lines, labels, **kwargs)

    
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
    
    
    def LSQ(self, x, y):
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
                from PIL import Image # pillow library --> MOVED DOWN TO IMPORT SWITCH
                ax.imshow(Image.open(img)) # no rotation, theoretically slower
            elif engine=="cv":
                import cv2 # python-opencv library - linux:pip install opencv-python --> MOVED DOWN TO IMPORT SWITCH
                ax.imshow(cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2RGB)) # auto-rotation, slower on older machine i think
            else:
                print("programmer you fucked up imshow")
            #imgs.pop(0)
            
            
    def complete_gallery(self):
        """ gallery of current dir (calls listfiles-self.images) """
        self.listfiles()#list and store images in self
        self.gallery(imgs=self.images)
        
        
    def rotate_xticks(self, rotation, long=0, ha="right", autoscale=1):
        """ rotate ticks and fix visual offset if long i guess
            - ha and autoscale only get done if long is True

            application example from plot_mse_mx after imshow:
                
            # show all ticks
            ax.set_xticks(np.arange(len(xlabels)))
            ax.set_yticks(np.arange(len(ylabels)))
            # ... and label them with the respective list entries
            ax.set_xticklabels(xlabels, ha="right")#horizontal alignment
            ax.set_yticklabels(ylabels)
            
            self.rotate_xticks(45)
        """
        ax=self.get_ax()
    
        # first, rotate 
        #"empty" but sets rotation (_str of this obj returns "Text(0, 0, '')")
        for tick in ax.get_xticklabels():
            tick.set_rotation(rotation)
        
        # then check if longer
        if long:#longer ones might appear shifted to right - compensate!
            
            xticks=ax.get_xticks()
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
        
    def xlabel(self, label=""):
        self.get_ax().set_xlabel(label)

    def ylabel(self, label=""):
        self.get_ax().set_ylabel(label)
        
    def common_ax_labels(self,xlabel="",ylabel=""):
        """ add a big axis, hide frame """
        fig = self.get_fig()
        fig.add_subplot(111, frameon=False)
        # hide tick and tick label of the big axis
        plt.tick_params(labelcolor='none', which='both', top=False, bottom=False, left=False, right=False)
        plt.xlabel(xlabel)#("common X")
        plt.ylabel(ylabel)#("common Y")


    def nicergrid(self,y_major=20E6, y_minor=2.5E6, x_major=0.5, x_minor=0.1):
        """ add x,y grid based on spacings
            - x_minor
            - y_minor
            - x_major
            - y_major
        
        """
        ax = self.get_ax()

        #axis y         #we have: 20M on left and 2.5*20=50M on right
        ax.yaxis.set_major_locator(MultipleLocator(y_major))
        ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
        ax.yaxis.set_minor_locator(MultipleLocator(y_minor))
        self.enginerd_yaxis()
        #axis x         # 0.1 minor and 0.5 major
        ax.xaxis.set_major_locator(MultipleLocator(x_major))
        ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
        ax.xaxis.set_minor_locator(MultipleLocator(x_minor))
        self.enginerd_xaxis()
        #ax.grid("on")
        ax.grid(b=True, which='major', color='grey', linestyle='-', alpha=0.5)
        ax.grid(b=True, which='minor', color='grey', linestyle=':', alpha=0.5)


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
    def hist(self,*args,**kwargs):
        """ forward to mpl hist
        note: old patchy-draw stuff at bottom of myink as comment
        """
        return self.get_ax().hist(*args,**kwargs)

    def imshow(self,*args,**kwargs):
        """ forward to mpl imshow"""
        self.im = self.get_ax().imshow(*args,**kwargs) # for animate
        self.imims.append(self.im) # for common_cb_lims
        return self.im

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


    def autoscale_fig(self):
        """
        try to fit most text of axis ticks, labels, titles w.o. overlapping
        - usually works, only GUI panel might overlap still
        - alternatively, use subplots.adjust wspace hspace bottom top
        """
        plt.tight_layout()


    def boxplot(self, data, xlabels="", meanoffset=False, ylabel="", title="", make_canvas=True):
        """
        creates 2row subplot for a boxplot w many elements (e.g. RSSIs) and labeling

        forked from https://stackoverflow.com/questions/33328774/box-plot-with-min-max-average-and-standard-deviation
        """

        # # data conditioning # # 
        statistics = []
        for item in data:
            item = np.array(item).astype(np.float)
            mins = np.min(item)
            maxes = np.max(item)
            means = np.mean(item)
            std = np.std(item)
            statistics.append([mins, means, maxes, std])

        mins, means, maxes, std  = np.array(statistics).astype("float").T # unpack
        x=np.arange(len(data))

        if meanoffset:
            off=means
            ylabel+=", means subtracted"
        else:
            off=0

        # # plotting # #
        if make_canvas:
            self.subplots()
        # create stacked errorbars
        self.errorbar(x, means-off, std, fmt='ok', lw=3) # fat std
        self.errorbar(x ,means-off, [means - mins, maxes - means], fmt='.k', ecolor='gray', lw=1) # thin min-max

        # xy_labelling
        ax = self.get_ax()
        ax.set_ylabel(ylabel)
        ax.set_xticks(np.arange(len(xlabels)))
        ax.set_xticklabels(xlabels, ha="right")#horizontal alignment
        self.rotate_xticks(45, autoscale=0)
        self.title(title)
        self.autoscale_fig()


    def boxplot_summary(self, data=[], xlabels=None, ylabel=None, title=None):
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
        self.boxplot(data=data, xlabels=xlabels, title=title, ylabel=ylabel)

        # put overlay
        self.scatter(x,y)            


    # experienced kwargs error - if **kwargs used AND cmap="turbo_r" -> both are ignored
    def waterfall(self, mx=None, x_axis = None, ax=None, title=None, 
                    yticks=[], places=2, cb_label="mag (dB)", colorbar=True, **kwargs): #decimal "places" =2 # decimal acc
                        # why turbo - https://ai.googleblog.com/2019/08/turbo-improved-rainbow-colormap-for.html
        """ imshow of mx, aligning yticks
            input:
                - mx
                - x_axis
                - ..
            output:
                - mx (same as input)
            """
        
        ## process arguments ##
        #
        #ylegend = self.mylegend
        
        if "cmap" not in kwargs:#if switch exists
            kwargs["cmap"]="turbo_r"
        if "interpolation" not in kwargs: # interpol-none removes blurr
            kwargs["interpolation"]="none"
        if "cb_label" in kwargs:
            cb_label=kwargs["cb_label"]
            #and remove, to not confuse the artist (imshow)
            kwargs.remove("cb_label")
        
        if np.size(mx)<2 or np.size(x_axis)<2:
            raise Exception("matrix and x_axis input required!")
        magDBs = mx # input matrix     
        #mx = np.array(mx, dtype=float)# imshow extent error?
        #TypeError: ufunc 'isfinite' not supported for the input types, and the inputs could not be safely coerced to any supported types according to the casting rule ''safe

        ## plotting ##
        #
        ax = self.get_ax(ax) # might generate figure if none defined
        # "extent" doc
        #   - needed to set ticks and grid correctly (not shifted into centers)
        #   - can also label
        #   - (0,0) is upper left of imshow but extent is flipped on y
        #   - extent = (0+m, magDBs.shape[1]+m, magDBs.shape[0]+n, 0+n)# n,m freely chosen
        #   - print(extent)# with testdata: 0 1001 3 0

        if np.size(yticks)>0:
            #print("hello")
            if ((np.size(yticks)) == magDBs.shape[0]):
                extent = (np.min(x_axis), np.max(x_axis),np.max(yticks), np.min(yticks))
                #print("chosen dueto {}".format(magDBs.shape))
            else:
                extent = (np.min(x_axis), np.max(x_axis), magDBs.shape[0], 0)
                #print("unchosen A dueto {}".format(magDBs.shape))
        else:
            extent = (np.min(x_axis), np.max(x_axis), magDBs.shape[0], 0)
            #print("unchosen B dueto {}".format(magDBs.shape))
        
        #print(type(extent))#tuple
        self.imshow(magDBs, **kwargs, aspect="auto", extent=extent)#aspect makes it rect etc #aspect auto enables arbitrary axis limits
        cb = self.colorbar(cb_label)

        if not colorbar: # colors wrong even though cmap is in kwargs
            cb.remove() # mpl 3.5.1 removes :) but space issue
            #self.autoscale_fig() # usecase twinx(), does not work - colorbar1 space is deleted so it overlaps if 2nd colorbar deleted
        #else:
            #self.cbs.append(cb) # ToDo remove - unused
        #ax.grid()#interpol off sufficient

        self.title(title)
        #self.xlabel("bins from {}Hz to {}Hz".format(self.enginerd(min(x_axis)),self.enginerd(max(x_axis))))
        
        if places>0:
            self.enginerd_xaxis(places=places)#commenting out works
        self.rotate_xticks(45)

        np.matrix(magDBs)

        
    def ecke(self, hidesmallframes=False): # inspired by mpl official doc
        """
        make a subplot with a corner in left bot, 5 plots around
        - return
        """
        fig, axs = plt.subplots(ncols=3, nrows=3)
        gs = axs[1, 2].get_gridspec()
        # remove the underlying axes
        for axsi in axs[1:, :2]:
            for ax in axsi:
                ax.remove()

        # first dim: how much of y-axis: "0:" means everything starting from 0
        # second dim: how much of x-axis: (starting right)
        axbig = fig.add_subplot(gs[1:, :2]) 
        #axbig.annotate('Big Axes \nGridSpec[1:, -1]', (0.1, 0.5),
        #                xycoords='axes fraction', va='center')

        if hidesmallframes:
            for axsi in axs:
                for ax in axsi:
                    self.blank(ax)

        fig.tight_layout()

        # put axs inside
        #self.axs = np.array([axbig, axs], dtype="object")
        #self.axs = axbig, axs
        self.ax = axbig
        self.axs = axs

        self.axs = np.delete(self.axs, [3,4,6,7])

        self.ecke_axs = axs
        self.ax_i = -1 # HACK


# https://stackoverflow.com/questions/17212722/matplotlib-imshow-how-to-animate
    def make_im_gif(self, data, fn='test_anim.gif', fps=1, sec=4):
        """ takes last self.imshow handle and makes a gif
            - data: array of elements to pass to imshow instances
            - fn: filename
            - fps
            - sec
            CAUTION: last im's axis labeling stays!
        """
        im = self.im

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
            - ax: to wich ax (or axs-for-all) to attach to
            - cmap?
            """
        ax = self.get_ax(ax)

        # forward certian things to set_label
        kwargs2 = {}
        things = ["horizontalalignment"]
        for thing in things:
            if thing in kwargs:
                kwargs2[thing]=kwargs[thing]
                kwargs.pop(thing)

        cb=self.get_fig().colorbar(self.im,ax=ax, **kwargs) # ( ((3.4.2) , 3.5.1 require cb to have correct color with custom cb!?
        cb.set_label(label, **kwargs2)

        return cb

    def cb_remove(self,i=None):
        """ remove one or all colorbars, index i

            NOTE: DOESNT SEEM TO WORK UNLESS common_CB lims called, or sth
                    maybe needs some plt.update() or sth?
        """
        if i==None:
            for imim in self.imims:
                imim.colorbar.remove()
        else:
            imim = self.imims[i]
            imim.colorbar.remove()


    def common_cb_lims(self, data):
        """ 
            - finds common min/max of data
            - iterates over self.imim
            - sets common colorbar limits
            - resets self.imim
        """
        mymin=np.amin(data)
        mymax=np.amax(data)
        #print("{},{}".format(mymin,mymax))
        for imim in self.imims:
            imim.set_clim(mymin,mymax)
            #print(imim)
            #self.get_fig().colorbar(imim,ax=self.get_ax())
        self.imims=[]#del imshow refs after rescaling


    def reset_coordsys(self):
        """ CLEAN UP PREV PLOT RANDOM SPACING
            - e.g. histos have 0,0 on lower left and not 0,0 on upper right per def --> call before and after annotating it w plot 
        """ 
        self.get_ax().margins(0) # AFTER plot - 
        self.twinx() # new axes for both
        self.twiny()
        self.hidexy() # hide xy labels etc

    def G53(self):
        """ reset coord sys to absolute
            - forwarder to reset_coordsys
            """
        self.reset_coordsys()

    #</myinkc> - if an indent level is wrong fcts afterwards not defined!

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def tester(): # module test, superseeds ifdef-main (since used here for import shenanigans) #
    oldtest()
    test_fontsize()
    tickrot()
    stemmy()
    weigh_scatter()

def oldtest():    
    ele = myinkc()
    print(ele.defaultcolorlist())
    
    x = np.array([0, 1, 2, 5])
    y = np.array([-1, 0.2, 0.9, 2.1])
    
    k, d = ele.LSQ(x,y)
    
    #ele.subplots()
    #ele.plot_mag()#this is in thvsia
    plt.plot(x, y, 'o', label='Original data', markersize=10)
    #plt.plot(x, k*x + d, 'r', label='Fitted line', c=ele.defaultcolorlist())#this did not fucking work wtf why didn't i check or uncomment
    plt.legend()
    plt.show()
    
    ele.modlegend("hellO") # take some ax function to test ax property


def test_fontsize():
    large_title2()
    large_alltext()


def large_title2():
    ele = myinkc()
    #plt.subplots(nrows=2)
    ele.subplots(nrows=2)
    ele.title("regular size")
    ele.ax_onward()
    ele.rcparams_update({'font.size': 22})
    ele.title("biig")
    ele.show()


def large_alltext():
    ele = myinkc()
    ele.rcparams_update({'font.size': 22})
    ele.subplots(nrows=2)
    ele.title("regular size")
    ele.ax_onward()
    
    ele.title("biig")
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


def ecke_tester():
    # basic
    ele=myinkc()
    ele.ecke()
    ele.scatter([1,2,3,4],[1,2,1,0])

    for i in range(0,5):
        ele.ax_onward()
        ele.scatter(i,i)

    # images
    ele=myinkc()
    ele.ecke(hidesmallframes=True)
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


def get_pics():
    from PIL import Image
    pics = []

    # using PIL
    pics.append(Image.open("myfigures/stinkbug.webp")) # plt / PIL demo pic
    pics.append(Image.open("myfigures/pic.png"))

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
        
        figsizes = {"bigfig":[15,10], "medfig":[10,6.6], "widefig" : [2*6.4, 4.8], "tallfig" : [6.4, 2*4.8], "dwarffig" : [6.4, 4.8/2]}
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


#-#-# module test #-#-#
if testing:#call if selected, after defined, explanation see above
    #tester()

    #ecke_tester()
    #test_make_im_gif()
    mycanvassize_test()

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
