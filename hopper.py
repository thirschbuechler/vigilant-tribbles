#
# hopper class module
## this can superseed myfolderparser and has way better name

# ToDo - import mfp functions and make mfp inherit hopper


def dummy(*args, **kwargs):
    pass


class hopper(object):
    """ - goto subfolder
        - cleanup afterwards
        """

    def __init__(self, folder, myprint=dummy):
        self.folder = folder
        self.myprint = myprint
        
    def __del__(self):
        self.report("delete called, session ended")
    
    def __enter__(self):
        self.report("with-context entered")
        return self # unless this happens, object dies before reporting
    
    def __exit__(self, exc_type, exc_value, tb):
        self.report("with-context exited")
        self.__del__() # unless this happens, session doesn't get exited
        #return


    def report(self, *args):
        self.myprint(*args)


def testreader():
    with open("file.txt", "r") as f:
                print(f.readline())


if __name__ == '__main__': # test if called as executable, not as library, regular prints allowed   
    with hopper("testfolder") as hop0:
        testreader()
        with hopper("subfolder") as hop1:
            testreader()
            

            