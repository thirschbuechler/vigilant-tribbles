#
# hopper class module
## be a minimal-example

# ToDo - import mfp functions and make mfp inherit hopper

import os


def dummy(*args, **kwargs):
    pass


class portal(object):
    """ - enter a subfolder
        - cleanup afterwards
        - no hopping
        """

    def __init__(self, folder, myprint=dummy):
        self.myprint = myprint
        self.__enterdir=self.getpath() # neaded for cleanup!
        self.folder = folder


    def __del__(self):
        self.myprint("delete called, session ended")


    # with-context stuff #

    def __enter__(self):
        self.myprint("with-context entered")
        os.chdir(self.folder) # goto folder
        return self # unless this happens, object dies before reporting
    
    def __exit__(self, exc_type, exc_value, tb):
        self.myprint("with-context exited")
        os.chdir(self.__enterdir)
        self.__del__() # unless this happens, session doesn't get exited
        #return



    # helper fcts  #
    def getpath(self):
        """get current shell path (working directory location)"""
        return os.getcwd()


    def cleanup(self): # 
        """ reset current-path after doing traversing 
        """
        os.chdir(self.__enterdir)


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
