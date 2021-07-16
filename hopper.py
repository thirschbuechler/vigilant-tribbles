#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# %%
"""
hopper - traverse folders and ease file operations

Created on Mon May 18 21:06:39 2020
@author: thirschbuechler
"""
import os
from pathvalidate import sanitize_filepath

#-#-# module test #-#-#
testing=False # imports don't seem to traverse this before reaching EOF and complaining about undef_bool !?
if __name__ == '__main__': # test if called as executable, not as library    
    testing=True
    #tester()#since this is no fct definition, can't call this, also py has no forward-declaration option

try:
    import mystring as ms
    from portal import portal
except:
    try:
        import vigilant_tribbles.mystring as ms
        from vigilant_tribbles.portal import portal

    except:
        print("failed to import module directly or via submodule -  mind adding them with underscores not operators (minuses aka dashes, etc.)")




# ToDo - with-context stuff like __enter__ and __exit__,
# - getpath() in enter to set "scriptdir" to current scope's dir
# - cleanup() to release it back where it is expected to be!


def integritycheck():
    """ better call doctest """
    import doctest
    print("performing doctest test..")
    res=doctest.testmod() # process doctest methods
    print(res)
    print("attempted==succeeded, if no fails\n")


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
        
        self.myprint=dummy   
        

        if "folder" not in kwargs:

            kwargs["folder"]=defaultpath

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
        path = self.sanitize(path)#make windows compatible
        os.mkdir(path)     
    
    def cleanup(self): # 
        """ reset current-path after doing traversing 
            - setrootdir to scriptdir
            - cd there
        """
        self.setrootdir(self.scriptdir) 
        self.cd(self.scriptdir)
    
    def sanitize(self, s):
        return sanitize_filepath(s)


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
if testing:#call if selected, after defined, explanation see above
    integritycheck() #doctest   
    
    print("todo: test cd functions - like playing fetch with a dog")
    
    a = hopper()
    a.cd("myfigures")
    a.listfiles(myprint=print)
    print(a.images)

    # testing legacy mystring include
    print("\nnow, without extensions:")
    print(ms.removestringparts([".jpg",".png"],a.images ))

# %%
