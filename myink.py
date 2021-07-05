
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
from matplotlib.ticker import EngFormatter
#from matplotlib.patches import Arc, Circle

#from PIL import Image # pillow library --> MOVED DOWN TO IMPORT SWITCH
#import cv2 # python-opencv library - linux:pip install opencv-python --> MOVED DOWN TO IMPORT SWITCH

#from skimage import idata, icolor
#from skimage.transform import rescale, resize, downscale_local_mean


# my modules
#-#-# module test #-#-#
testing=False # imports don't seem to traverse this before reaching EOF and complaining about undef_bool !?
if __name__ == '__main__': # test if called as executable, not as library
    import myfolderparser as mfp
    testing=True
    #tester()#since this is no fct definition, can't call this, also py has no forward-declaration option
else:
    from vigilant_tribbles import myfolderparser as mfp
    #testing=False


## thing to make matplotlib access easier ###
class myinkc(mfp.myfolderparserc): 
    
    ## housekeeping
    def __init__(self, *args, **kwargs):
        #plt.close("all")
        # note: matplotlib may need to be reloaded to quit xkcd mode
        #importlib.reload(plt) # not required anymore (using with-context)
        self.ax = None
        self.fig = None
        
        
        self.printimg=True#shall images be printed
        self.yright=None#var to be inspected on plot cleanup and reset
        
        
        super().__init__(*args, **kwargs) # superclass init, in case there is any
        
        
    def subplots(self, *args, **kwargs):
        self.fig, self.axs = plt.subplots(*args, **kwargs)
        self.ax_i = 0
        
        
        if not (hasattr(self.axs, "__iter__")):#case axs was ax only #np.size didn't work for 2d axs
            self.ax=self.axs#put singular here    
            self.axs=np.array([self.axs])# axs list here - enable parsing always
        
        else: # case axs is list already
            self.axs=self.roadkill(self.axs) #remove any dimensions    
            self.ax=self.axs[0]
            
        return self.fig, self.axs
    
    
    # close old plots    
    def close(self, st="all"):
        plt.close(st)
    
    # show last plots - for non-spyder IDEs which need manual trigger
    def show(self):
        plt.show()
    
    
    def rcparams_update(self,dict):
        plt.rcParams.update(dict)
        #e.g. this as
        #plt.rcParams.update({'font.size': 22})
        #self.rcparams_update({'font.size': 22})
    
    
    def savefig(self,*args, **kwargs):
        plt.savefig(*args, **kwargs)


    def ax_onward(self):
        self.ax_move(1)
        return self.ax
        
    
    def ax_backtrack(self):
        self.ax_move(-1)
        return self.ax
    
    
    def roadkill(self, thing): # flaten if possible - remove any dimensions and make a list
        if (hasattr(thing, "__iter__")):
            return(thing.flatten()) # even more powerful: thing = np.concatenate(thing).ravel()
        else:
            return thing
    
            
    def ax_move(self, where):
        self.ax_i = self.ax_i + where
        
        self.axs = self.roadkill(self.axs)
        
        if np.size(self.axs)==0:
            raise Exception("only one axis - can't iterate")
        self.ax = self.axs[self.ax_i]
        return self.ax
    
    
    #function, since pos in axs will change during plotting
    #!! generates figure if none (no plt.figure() or self.subplots() etc. called beforehand)!! ergo be inside doplot()-if-context
    def get_ax(self, ax=None): # get class' ax or check if ax is passed and route through
        if ax is None: # no axis given
            if type(self.ax) is type(None): # is axis not a property already - robust
                ax=plt.gca() #  get current axis $$ this might give multiple.. wtf$$ no the error was probably self.ax=self.axs[0] above
                #print("gca")
            else:    
                ax=self.ax # if its a property take that
                #print("returning directly")
        return ax
    
    
    def set_ax(self, ax=None): # set class' ax via parameter or matplotlib poll
        if ax is None: # no axis given
            self.ax=plt.gca() #  get current whatever
        else:
            self.ax=ax
    
    
    # made for comradelegend only, right now
    def get_fig(self, fig=None): # get class' fig or check if fig is passed and route through
        if fig is None: # no axis given
            if type(self.fig) is type(None): # is axis not a property already - robust with type
                fig=plt.gcf() #  get current whatever $no setting - does it matter
            else:    
                fig=self.fig # if its a property take that
        return fig
    
    
    def set_fig(self, fig=None): # set class' fig via parameter or matplotlib poll
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
    
    
    def suptitle(self, title=""):# major title/label for figure == "supertitle", to be fig.suptitle compatible
        fig = self.get_fig()
        fig.suptitle(title)
        
    
    def figlabel(self, title=None):#alias for what it actually does, avoids confusion
        if title!=None:    
            self.suptitle(title)
            
    
    def title(self, title=None): # minor title of individual axis
        ax = self.get_ax()    
        if title!=None:    
                ax.set_title(title)
        
    
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
        

    def enginerd(self, value, unit='Hz', **kwargs):####todo: enginerd object instead of calling it this badly here and axis wise
        # load defaults if necessary
        if not "places" in kwargs:
            kwargs["places"]=2 # decimal acc
        if not "sep" in kwargs:
            kwargs["sep"]="\N{THIN SPACE}"
            
        return(EngFormatter(**kwargs).format_eng(value))
    
        
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
        #for stuff in [ax.get_legend()]:
        #   stuff.remove()
        oh_my = ax.get_legend() # alt
        if oh_my:
            oh_my.remove()


    def killxlabel(self, ax=None):
        ax = self.get_ax(ax)
        ax.set_xticklabels([]) # remove numbers
        ax.set_xlabel("") # remove text (unit)
        
        
    def modlegend(self, mylegendtext=None, addtext=None, title=None, rmsubstr=None, ax=None, *args, **kwargs):#, *args, **kwargs for ax.legend only
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
                mytext=mfp.removestringparts(rmsubstr,mytext)
                print(mytext)
                
            mytext.insert(0,title) # insert as first ele into list
            legendlines=ax.get_lines()[:] # decompose simple_list object, or sth.
            legendlines.insert(0,extra) # insert into regular list
            
            
            #print(mytext)
            #print()
            
            ax.legend(legendlines, mytext)   
    
    
    def comradelegend(self, fig=None, **kwargs): # collect all labels of one figure and collate to one master legend
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
        lines_labels = [ax.get_legend_handles_labels() for ax in fig.axes]
        lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
        # kill old legends
        for ax in fig.axes:
            self.killlegend(ax)
                
        # finally we invoke the legend 
        fig.legend(lines, labels, **kwargs)
        
        
    def comradeaxlegend(self, ax=None, **kwargs): # collect all labels of one figure and collate to one master legend
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
    # vertical lines #
    def vmarkers(self, start, stop, col, ax=None):
        ax = self.get_ax(ax)
        ylims=ax.get_ylim()
        ax.vlines(start,  ylims[0], ylims[1], colors=col)
        ax.vlines(stop,  ylims[0], ylims[1], colors=col)
        

    # horz lines #        
    def hmarkers(self, start, stop, col, ax=None):
        ax = self.get_ax(ax)
        xlims=ax.get_xlim()
        ax.hlines(start,  xlims[0], xlims[1], colors=col)
        ax.hlines(stop,  xlims[0], xlims[1], colors=col)
        

    # mixture of keyworded and non-keyworded arguments, aswell as routing not everything through makes this not practical
    # does what it says on the tin -- 
    #  $todo: if figure creation happens in thsmith via fct, has to be triggered as well         
    #def xkcd_ify(self, fct=plt.plot, *args, **kwargs):
    #    with plt.xkcd():
    #       fct(*args, **kwargs)


    # marker helper            
    def markernum(self, num):
        num=num+2 # skip first two horz matplotlib markers unless too many
        while(num>11): # ensure matplotlib markers don't overflow
            num=num-12
        return num
    
    
    def del_nonnum(self, a):
        return re.sub('[^0-9.]','', a)
    

    def killall(self):
        plt.close("all") # fun but not needed
                    
    
    def LSQ(self, x, y):
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
            print("something fucked up - points are no list in list_to_xy")
        

    def resetcolorwheel(self):
        self.get_ax().set_prop_cycle(None)#restart auto-"colorwheel" for line-colors
        

    def defaultcolorlist(self, maxval=""):
        dictlist=[]
        for value in list(plt.rcParams["axes.prop_cycle"]):
            dictlist.append(value["color"])

        if maxval!="":
            while len(dictlist) > int(maxval):
                dictlist.pop()
    
        return dictlist
    
    
    def include_me(self, left, right, me): # get two bound and tertiary value, if third out of bounds include the third
        # example use
        #left, right = ax.get_xlim() 
        #left, right = self.include_me(left, right)
        #ax.set_xlim(left, right) e
        
        if me < left:
            left=me*1.1
        elif me > right:
            right=me*1.1
            
        return left, right
    

    def picframe(self, *args, **kwargs): # unused atm, maybe into picshow at some time
        kwargs["dpi"]=300
        return self.subplots(*args, **kwargs) # a new figure/axis has to be explicitly added; figsize in inches BUT degrades only
    
    
    def gallery(self, imgs= []): # takes a list (!) of one or more elements and splits it up into 2x2 max.
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
        self.listfiles()#list and store images in self
        self.gallery(imgs=self.images)
        
        
    def rotate_xticks(self, rotation, long=0, ha="right", autoscale=1):#ha and autoscale only get done if long is True
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
        self.get_fig().subplots_adjust(*args, **kwargs)   
        
        
    def hide_frame(self,ax=None):
        self.get_fig().patch.set_visible(False)
        self.get_ax(ax).axis('off')

    def blank(self,ax=None):
        self.hide_frame(ax=ax)
        
        
    def common_ax_labels(self,xlabel="",ylabel=""):
        # add a big axis, hide frame
        fig = self.get_fig()
        fig.add_subplot(111, frameon=False)
        # hide tick and tick label of the big axis
        plt.tick_params(labelcolor='none', which='both', top=False, bottom=False, left=False, right=False)
        plt.xlabel(xlabel)#("common X")
        plt.ylabel(ylabel)#("common Y")
        
        
def tester(): # module test, superseeds ifdef-main (since used here for import shenanigans) #
    #oldtest()
    #test_fontsize()
    tickrot()


def oldtest():    
    ele = myinkc()
    print(ele.defaultcolorlist())
    
    x = np.array([0, 1, 2, 5])
    y = np.array([-1, 0.2, 0.9, 2.1])
    
    k, d = ele.LSQ(x,y)
    
    #ele.subplots()
    #ele.plot()#this is in thvsia
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
    ele.subplots(nrows=2) # why roadkill not defined? is a self-method of myinkc !? no forward-decl possible in py.. - because rcparams-update was at wrong indent level..
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


#-#-# module test #-#-#
if testing:#call if selected, after defined, explanation see above
    tester()