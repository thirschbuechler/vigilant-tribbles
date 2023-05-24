# -*- coding: utf-8 -*-
"""
Fruitseed_FF.py 

A container for data, metadata, histograms, etc.

eg.
Fruit "RSSI"
- data
- x
- meta
- hist
- x_hist
- 
- condition (C/E/none)
..


Created 230523

@author: thirschbuechler
"""


class Fruit(object):
    #__metaclass__ = GetAttr
    def __init__(self, ID=None, stem=None, 
                    data=[], data_x=[], hist=[], hist_bins=[], metadata={},
                        **kwargs):
        #super().__init__(**kwargs) # (*args, **kwargs) # superclass inits
        
        self.stem = stem
        self.ID = ID

        self.fruits = {} # dict of ID:obj

        # every Fruit has metadata
        self.metadata = metadata
        # if not root node, then it has props
        if self.stem:
            self.data = data
            self.data_x = data_x
            self.hist = hist
            self.hist_bins = hist_bins
        
    def __getitem__(self, obj):
        return self.fruits[obj]
    def __len__(self):
        return len(self.fruits.items())
    

    # def __call__(self, *args, **kwargs):
    # unused, tried with enum.Enum as rootclass,
    # but won't accept additional init args/kwargs


    def __str__(self):
        return self.ID
    
    def __iter__(self):
        
        return iter(self.fruits.values()) # fruits is ID:obj, so return objs

    def mod(self, dict={}):
        """ hack - to quickly add/mod dict items, aka class variables"""
        self.__dict__.update(dict)

    def sprout(self, *args, **kwargs):
        """make a fruit on this supposed tree"""
        if "ID" in kwargs:
            ID = kwargs["ID"]
        elif args:
            ID = args[0]
        else:
            raise Exception("need ID for new Fruit")
    
        # put it into fruits-dict
        self.fruits.update({ID:Fruit(*args, **kwargs)})
        # also make it an attribute
        self.__dict__.update(self.fruits)


    def get_meta(self):
        """ get root's (stem) metadata and update with own """
        if self.stem.metadata:
            meta = self.stem.metadata
        else:
            meta = {}
        meta.update(self.metadata)
        return meta





def fruittester():
    """
    >>> fruittester()
    Apple
    Apple
    Apple
    Apple
    {'color': 'red', 'origin': "Joe's"}
    Bpple
    Bpple
    {'color': 'green', 'origin': "Joe's"}
    
    """
    # # setup 
    
    # root node
    root = Fruit("rottenapple", metadata={"color":"black", "origin": "Joe's"})
    # sprout branches
#-#-# module test #-#-#
if __name__ == '__main__': # test if called as executable, not as library
    
    root = Fruit("rottenapple", metadata={"color":"black", "origin": "Joe's"})

    #Apple = Fruit("Apple",root, metadata={"color":"red"})
    #Bpple = Fruit("Bplle", root, metadata={"color":"green"})
    #root.mod({"fruits":[Apple, Bpple]})
    #print(root.__dict__)

    root.sprout("Apple",root, metadata={"color":"red"})
    
    root.sprout("Bpple",root, metadata={"color":"green"})
    

    # # testdrive
    
    # class subscriber
    print(root["Apple"])
    # class attributes
    print(root.Apple)

    # class iterator
    for item in root:
        print(item)
        #print(item["ID"]) class subscriber redirects to self.fruits, so this doesn't work
        print(item.ID)
        print(item.get_meta())


def integritycheck():
    """ better call doctest """
    import doctest
    print("performing doctest test..")
    res=doctest.testmod() # process doctest methods
    print(res)
    print("attempted==succeeded, if no fails\n")


#-#-# module test #-#-#
if __name__ == '__main__': # test if called as executable, not as library
    #fruittester()
    integritycheck()
