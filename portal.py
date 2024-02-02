#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
portal - enter folder via with-context, cleanup when leaving
hopper (child class) - traverse folders and ease file operations

Created on Mon May 18 21:06:39 2020
@author: thirschbuechler
"""
import sys, os
from pathvalidate import sanitize_filepath


# import modules if in parent directory via path tmp
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vigilant_tribbles import Fruit
from vigilant_tribbles import mystring as ms

# undo path tmp import
sys.path.pop(len(sys.path)-1)




def integritycheck():
    """ better call doctest """
    import doctest
    print(f"doctest called in ({__file__})")
    res=doctest.testmod() # process doctest methods
    print(res)
    print("attempted==succeeded, if no fails\n")



def dummy(*args, **kwargs):
    pass

# here: child of Fruit.Fruit for data collection purposes,
# class portal(object) etc. will work as well
class portal(Fruit.Fruit):
    """ - enter a subfolder
        - cleanup afterwards
        - no hopping
        """

    def __init__(self, folder="", myprint=dummy, **kwargs):
        self.myprint = myprint
        self.__enterdir=self.getpath() # needed for cleanup!
        #self.cd(self.__enterdir) # for some reason, a cd of a sub-loop with a portal would fail (it assumes start from scriptdir) - nope was different rooted obj i think
        self.folder = folder

        super().__init__(**kwargs) # (*args, **kwargs) # superclass inits


    def __del__(self):
        self.myprint("delete called, session ended")


    # with-context stuff #

    def __enter__(self):
        self.myprint("with-context entered")
        if self.folder!="":
            self.cd(self.folder) # goto folder
        return self # unless this happens, object dies before reporting
    
    def __exit__(self, exc_type, exc_value, tb):
        self.myprint("with-context exited")
        self.cd(self.__enterdir)
        self.__del__() # unless this happens, session doesn't get exited
        #return



    # helper fcts  #
    def getpath(self):
        """get current shell path (working directory location)"""
        return os.getcwd()

    def cd(self, newpath):
        """ wrap chdir 
        - slightly more readable exceptions
        - folder:x.bin notation possible
        """

        # bin override via ":" notation possible
        if ".bin" in newpath:
            newpath = newpath.split(":")[0] # eg folder:0.bin
            #print("bla is ".format(bla))

        now=self.getpath()
        newpath_abs=os.path.join(now,newpath)

        if os.path.exists(newpath):
            os.chdir(newpath)
        elif os.path.exists(newpath_abs):
            os.chdir(newpath_abs)
        elif (newpath in now):
            #raise Exception("dude you are already there")
            self.myprint("dude you are already there")
            #pass
        else:
            raise Exception("neither abs nor relative {} exists, now: {}".format(newpath,now))
        # note: a "\\ error" (\\ occouring in path not found) usually means the path is invalid (not escape issue or sth)


    def cleanup(self): # 
        """ reset current-path after doing traversing 
        """
        self.cd(self.__enterdir)





class hopper(portal):
    """
    thing to traverse directorys
    - go there (cd functions)
    - list files and classify them
    - if an file-open called by any function, the path can be omitted there
    """
    
    # class init
    def __init__(self, *args, **kwargs):  
        if "defaultpath" in kwargs:
            defaultpath = kwargs["defaultpath"]
        else:
            defaultpath=self.getpath() # py-file folder if not declared
            
        self.scriptdir=defaultpath #NEVER EVER CHANGE - needed foor cleanup!
        self.rootdir=defaultpath # change as you please
        
        self.myprint=ms.dummy   
        
        
        #if not ("folder" in kwargs): #$$ dunno why but this didn'work - instead multiple folder-keys were created or sth - made defaultparam for "folder" in portal init
            #kwargs["folder"]=defaultpath

        #print("hopper folder is {}".format(kwargs["folder"]))
        super().__init__(*args, **kwargs) # superclass init, in case there is any
    
    
    def set_myprint(self,handle):
        self.myprint=handle
    

    # helper fcts  #
    

    def setrootdir(self, newpath=""):
        """ change reset target of cdres, cdleap, .. root of folders to traverse"""
        if newpath!="":
            self.rootdir = newpath
        else:
            self.rootdir = self.getpath()
        self.myprint("rootdir from {} to {}".format(self.rootdir,newpath))
    

    def cdup(self):
        self.cd('../')
        
    def cdres(self):
        """ reset to rootdir for further folder traversing"""
        self.cd(self.rootdir)
    
    def cdleap(self, newpath):
        """ leap-jump over to other dir after cdres to rootdir"""
        self.cdres()
        self.cd(newpath)

    def mkdir(self, path):
        """ input path to make dir """
        path = self.sanitize(path)
        os.mkdir(path)     
    
    def cleanup(self): # 
        """ reset current-path after doing traversing 
            - setrootdir to scriptdir
            - cd there
        """
        self.setrootdir(self.scriptdir) 
        self.cd(self.scriptdir)
    
    def sanitize(self, s):
        """ fix common path and filename character issues """
        s = sanitize_filepath(s) # most issues solved
        s = s.replace("/", "") # don't get folders by a desanitzed slash-n
        s = s.replace(" ","_") # no spaces allowed - to facilitate easier shell processing
        return s


    def get_dp(self, subfolder=""):
        """dropbox importer over home dir"""
        # prep vars
        dp_f=os.path.join("~","Dropbox")
        dp_f = (os.path.expanduser(dp_f))# C:\Users\hirschbuechler\Dropbox # however IS Dropbox.lnk
        #print(os.path.exists(dp_f)) # False, is Dropbox.lnk not folder!

        if os.path.exists(dp_f):
            path=dp_f
        else:
            file="Dropbox.txt"
            file=os.path.expanduser(os.path.join("~",file))
            #path=file
            if not os.path.exists(file):
                raise Exception("no file {}".format(file))
            try:
                with open(file,"r") as f:
                    path = f.read()
            except Exception as e:
                print("reading {} failed, dueto {}".format(file,str(e)))

        if not os.path.exists(path):
            raise Exception("The folder read from {} is not existant (on this computer)".format(str(path)))
        else:
            return path


    def goto_dp(self, subfolders=[], show=False):
        """dropbox importer over home dir and going places (there)"""
        dp_f = self.get_dp()
        #print(dp_f)

        # goto dropbox
        self.cd(dp_f)

        # set working dir to..
        for sub in subfolders:
            self.cd(sub)

        if show:
            # what's here?
            self.listfiles(myprint=print)


    def listfiles(self,myprint=ms.dummy): 
        """ list files and classify them """
        #https://stackoverflow.com/questions/18262293/how-to-open-every-file-in-a-folder
        location = self.getpath()
        counter = 0 #keep a count of all files found
        otherfiles = [] #list to keep any other file that do not match the criteria
        
        self.images=[]
        self.layouts=[] # pyweave pmd layout files
        self.touchstone=[]
        self.csv=[]
        self.pti_files=[]
        
        for file in os.listdir(location):
            try:
                if file.endswith(".png") or file.endswith(".jpg"):
                    self.images.append(file)
                    counter +=1
                elif file.endswith(".pmd"):
                    self.layouts.append(file)
                    counter +=1
                elif file.endswith(".s2p") or file.endswith(".s1p"):
                    self.touchstone.append(file)
                    counter +=1
                elif file.endswith(".csv") or file.endswith(".isd"):
                    self.pti_files.append(file)
                    if file.endswith(".csv"):
                        self.csv.append(file)
                    counter +=1
                else:
                    otherfiles.append(file)
                    #myprint("not classified: {}".format(file))
                    counter +=1
            except Exception as e:
                print("No files found here!")
                raise e
        
        myprint("classified {}/{} files".format(counter-len(otherfiles),counter))


    def get_bins(self, folder, fext=""):
        """ get [bins,keys] of fext in a folder
            - bins: dict, bins
                eg all run1_i.bin files, for any i
            - keys: to access dict of runs
                eg run0..run99
            - other kwargs: ignored
        """

        # get files
        files = self.humanlist_fext(folder,fext)

        # find all sets
        bins = ms.groupByPrefix(files)
        keys = [key for key in bins.keys()]

        return bins,keys


    def humanlist_fext(self,folder,fext="s2p"):
        """ find all s1p,s2p or csv files in folder"""
        
        with portal(folder):
            # find stuff and classify it
            self.listfiles(myprint=ms.dummy)
            
            # select which found classifier to use
            if fext=="s2p" or fext=="s1p" or fext==[]:
                files=ms.sort_human(self.touchstone)    
            elif fext=="csv":
                files=ms.sort_human(self.csv)  
            else:
                raise Exception("humanlist - no valid fext selected")
            
            return files
        
        
    def human_bin_list(self, bins="",keys="", **kwargs):
        """ print keys n bins nicely 
            - folder
            - sparams
            - myprint - optional
            - bins, keys - optional
        """
        if (bins=="" and keys==""):
            # fetch
            bins,keys = self.get_bins(**kwargs)
        elif (bins=="" or keys==""):
            raise Exception("either provide no bins, keys (fetch them via folder) or both")
        else:
            # bins and keys are given values
            pass
        
        txt = [("{}: {}".format(key,len(bins[key]))) for key in keys]
        return(txt)
    


#### testing stuff ####

def testreader():
    with open("file.txt", "r") as f:
                print(f.readline())

def portaltests():
    print("hello") 

    os.chdir("vigilant_tribbles") # for some reason if called as main but script seated as submodule in another git, the path is the root-project and not submodule
    with portal("testfolder", myprint=print) as p1:
        print("hello2")
        print(p1.getpath())
        testreader()
        with portal("subfolder") as p2:
            testreader()
        testreader()


def hoppertests():
    print("todo: test cd functions - like playing fetch with a dog")
    
    a = hopper()
    a.cd("myfigures")
    a.listfiles(myprint=print)
    print(a.images)

    # testing legacy mystring include
    print("\nnow, without extensions:")
    print(ms.removestringparts([".jpg",".png"],a.images ))


    
#-#-# module test #-#-#
if __name__ == '__main__': # test if called as executable, not as library    
    integritycheck() #doctest   

    #portaltests()
    #hoppertests()
    



