#
# hopper class module
## be a minimal-example

# ToDo - import hoppy functions and make hoppy inherit hopper

import sys, os

# import modules if in parent directory via path tmp
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vigilant_tribbles import Fruit

# undo path tmp import
sys.path.pop(len(sys.path)-1)



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


#### testing stuff ####

def testreader():
    with open("file.txt", "r") as f:
                print(f.readline())


if __name__ == '__main__': # test if called as executable, not as library, regular prints allowed  
    print("hello") 

    os.chdir("vigilant_tribbles") # for some reason if called as main but script seated as submodule in another git, the path is the root-project and not submodule
    with portal("testfolder", myprint=print) as p1:
        print("hello2")
        print(p1.getpath())
        testreader()
        with portal("subfolder") as p2:
            testreader()
        testreader()
