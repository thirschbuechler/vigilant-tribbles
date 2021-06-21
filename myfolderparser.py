#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Myfolderparser - traverse folders and ease file operations

Created on Mon May 18 21:06:39 2020
@author: thirschbuechler
"""
import os
from mystring import * # legacy compatibility for every external call to mfp

# ToDo - with-context stuff like __enter__ and __exit__,
# - getpath() in enter to set "scriptdir" to current scope's dir
# - cleanup() to release it back where it is expected to be!
# - bump issue

def integritycheck():
    """ better call doctest """
    import doctest
    print("performing doctest test..")
    res=doctest.testmod() # process doctest methods
    print(res)
    print("attempted==succeeded, if no fails\n")


class myfolderparserc(object):
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
            
        self.scriptdir=defaultpath #NEVER EVER CHANGE - neaded foor cleanup!
        self.rootdir=defaultpath # change as you please
        
        self.myfprint=dummy   
        
        super().__init__(*args, **kwargs) # superclass init, in case there is any
    
    
    def set_myfprint(self,handle):
        self.myfprint=handle
    

    # helper fcts  #
    def getpath(self):
        """get current shell path (working directory location)"""
        return os.getcwd()
    

    def setrootdir(self, newpath):
        """ change reset target of cdres, cdleap, .. root of folders to traverse"""
        self.rootdir = newpath
        self.myfprint("rootdir from {} to {}".format(self.rootdir,newpath))
    

    def cd(self,newpath): 
        self.myfprint("cd from {} to {}".format(self.getpath(),newpath))
        try:
            #if(os.path.isdir(newpath)):
            #print("going to {}".format(newpath))
            #os.chdir(os.path.dirname(newpath)) # change current shell path             
            #newpath=os.path.join(self.getpath(),newpath)
            if "//" in newpath:
                raise Exception("don't escape windows style, use os.path.join pls!!")
            os.chdir((newpath)) # change current shell path                
        except Exception as e:
            pnow=self.getpath()
            raise Exception("folder {} not found, currently in {}  (os.path isdir true on second, tip: set rootdir and jumpdirs & don't traverse zigzag in different levels, cleanup after blocks'), ".format(e, pnow))
    
    def cdup(self):
        self.cd('../')
        
    def cdres(self):
        """ reset to rootdir for further folder traversing"""
        self.cd(self.rootdir)
    
    def cdleap(self, newpath): # leap-jump over to other dir after topdir
        self.cdres()
        self.cd(newpath)
    
    def cleanup(self): # reset current-path to scriptdir after doing some traversing
        self.setrootdir(self.scriptdir) 
        self.cd(self.scriptdir)
    

    def listfiles(self,myprint=dummy): 
        """ list files and classify them """
        #https://stackoverflow.com/questions/18262293/how-to-open-every-file-in-a-folder
        location = self.getpath()
        counter = 0 #keep a count of all files found
        otherfiles = [] #list to keep any other file that do not match the criteria
        
        self.images=[]
        self.layouts=[] # pyweave pmd layout files
        self.touchstone=[]
        
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
                else:
                    otherfiles.append(file)
                    myprint("not classified: "+file)
                    counter +=1
            except Exception as e:
                print("No files found here!")
                raise e
        
        myprint("found {} files in total".format(counter))


#-#-# module test #-#-#
if __name__ == '__main__': # test if called as executable, not as library
    integritycheck() #doctest   
    
    print("todo: test cd functions - like playing fetch with a dog")
    
    a = myfolderparserc()
    a.cd("myfigures")
    a.listfiles(myprint=print)
    print(a.images)

    # testing legacy mystring include
    print("\nnow, without extensions:")
    print(removestringparts([".jpg",".png"],a.images ))
