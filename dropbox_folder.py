#
#from vigilant_tribbles import myfolderparser as mfp
import myfolderparser as mfp
import os


def get_dropbox(subfolder=""):
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

    #dp_f = os.path.abspath(dp_f) # turn any .lnk into path etc.
    #dp_f = os.readlink(str(dp_f+".lnk")) # turn any .lnk into path etc.
    #dp_f = os.startfile("C:\\Users\\hirschbuechler\\Dropbox.lnk") # opens explorer

    #hardcoded="C:\\Users\\hirschbuechler\\Dropbox.lnk"
    #dp_f = os.readlink(hardcoded)
    #print(os.path.exists(hardcoded))
    #with open(hardcoded,'r') as f:
    #    dp_f=f.read()
    
    if not os.path.exists(path):
        raise Exception("The folder read from {} is not existant (on this computer)".format(str(path)))
    else:
        return path


def goto_subfolder(subfoolders=[], show=False):
    """dropbox importer over home dir and going places (there)"""
    dp_f = get_dropbox()
    print(dp_f)

    # make parser
    pe = mfp.myfolderparserc()
    pe.setrootdir(pe.getpath())

    # goto dropbox
    pe.cd(dp_f)

    # set working dir to..
    for sub in subfoolders:
        pe.cd(sub)

    if show:
        # what's here?
        pe.listfiles(myprint=print)


#-#-# module test #-#-#
if __name__ == '__main__': # test if called as executable, not as library
    goto_subfolder(show=True)