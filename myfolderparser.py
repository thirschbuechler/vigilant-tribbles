#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 18 21:06:39 2020

@author: thirschbuechler
"""

        #cleanup to avoid traverse issue - this should be integrated into mfp!!
        #self.setinitdir(myinitcd) 
        #self.cd(myinitcd)
        
        
import os

def integritycheck():
    import doctest
    print("performing doctest test..")
    res=doctest.testmod() # process doctest methods
    print(res)
    print("attempted==succeeded, if no fails\n")
    
def dummy(*args, **kwargs):
    pass

def iscontainedin(matchers, listt): # returns matches by modding listt
    return [s for s in listt if any(xs in s for xs in matchers)]


def removecontainingof(tobe_del,listt, sure=0): # removes stuff from listt
    if type(listt)!=list and sure==0:
        print("are you sure to hand over a non-list?")
        print("nothing happened")
    else:
        matches=iscontainedin(tobe_del,listt)
        for s in matches:
            listt.pop(listt.index(s))


def removestringparts(matchers, listt): 
    """returns cleaned list of input listt (list) and to-be-removed matchers (list)
    
    >>> removestringparts("QQ",["QQasdf","asdfQQasdf"])
    ['asdf', 'asdfasdf']
    
    >>> removestringparts(["QQ","s"],["QQasdf","asdfQQasdf"])
    ['adf', 'adfadf']
    """
    #print("hi")
    if type(matchers)==str:
        matchers=[matchers]#assume if a string given to only replace the whole thing
    
    for matcher in matchers:
        listt = [line.replace(matcher,"") for line in listt]  # replace with nothing
        #print(line)
    return listt


## thing to parse directorys 
class myfolderparserc(object):
        
    ## housekeeping
    def __init__(self, *args, **kwargs):  
        if "defaultpath" in kwargs:
            defaultpath = kwargs["defaultpath"]
        else:
            defaultpath=self.getpath() # py-file folder if not declared
            
        self.initdir=defaultpath 
        self.myfprint=dummy        
        super().__init__(*args, **kwargs) # superclass init, in case there is any
        
    def set_myfprint(self,handle):
        self.myfprint=handle
        
    # helper fcts  #
    def getpath(self):
        return os.getcwd() # get current shell path
    
    def setinitdir(self, newpath): # change reset target of cdres
        self.initdir = newpath
        self.myfprint("from {} to {}".format(self.getpath(),newpath))
        
    def cd(self,newpath): 
        self.myfprint("from {} to {}".format(self.getpath(),newpath))
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
            raise Exception("folder {} not found, currently in {}  (os.path isdir true on second, tip: set initdir and jumpdirs & don't traverse zigzag in different levels, cleanup after blocks'), ".format(e, pnow))
        
    def cdup(self):
        self.cd('../')
        
    def cdres(self): # reset
        self.cd(self.initdir)
        
    def cdleap(self, newpath): # leap-jump over to other dir after topdir
        self.cdres()
        self.cd(newpath)
        
        
    def listfiles(self,myprint=dummy): # list files and save imgs in new
    #https://stackoverflow.com/questions/18262293/how-to-open-every-file-in-a-folder
        location = os.getcwd() # get present working directory location here
        counter = 0 #keep a count of all files found
        otherfiles = [] #list to keep any other file that do not match the criteria
        
        self.images=[]
        self.layouts=[]#pmd layout files
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
                raise e
                print("No files found here!")
        myprint("found {} files in total".format(counter))
 

      
#-#-# module test #-#-#
if __name__ == '__main__': # test if called as executable, not as library
    integritycheck()    
    
    print("todo: test cd functions - like playing fetch with a dog")
    
    
    a = myfolderparserc()
    a.cd("myfigures")
    a.listfiles(myprint=print)
    print(a.images)