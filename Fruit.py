# -*- coding: utf-8 -*-
"""
Fruitseed_FF.py 

A container for data, metadata, histograms, etc.

eg.
Tree "RSSI-msr"
    - meta
        - date
        - antenna type
        - ...
    - Fruit "RSSI"
        - data
        - x
        - meta
            - (inherited meta)
            - condition (C/E/none)
        - subFruit "hist"
            - data
            - x
    - 
    
    ..


Created 230523

@author: thirschbuechler
"""
class Fruit(object):
    #__metaclass__ = GetAttr
    def __init__(self, ID=None, stem=None, 
                    data=[], data_x=[], metadata={}
                        ):
        #super().__init__(**kwargs) # (*args, **kwargs) # superclass inits
        
        self.stem = stem # root obj
        self.ID = ID # name of this container

        self.fruits = {} # dict of ID:obj of sub-objects

        # every Fruit has metadata
        self.metadata = metadata
        # if not root node, then it has props
        
        #self.__dict__["data"] = data
        self.data = data
        self.data_x = data_x
        
    def __getitem__(self, obj): # Attribute handler
        return self.__dict__[obj]
    
    def __len__(self):
        return len(self.fruits.items())
    

    # def __call__(self, *args, **kwargs):
    # unused, tried with enum.Enum as rootclass,
    # but won't accept additional init args/kwargs


    def __str__(self):
        return self.ID
    
    def __iter__(self): # Iterator: called on "for item in Fruit"
        return iter(self.fruits.values()) # fruits is ID:obj, so return objs

    def mod(self, dict={}):
        """ hack - to quickly add/mod dict items, aka class variables"""
        self.__dict__.update(dict)

    def sprout(self, *args, **kwargs):
        """make a fruit on this object,
            be it a tree (no parent stem),
            or another fruit
            """
        if "ID" in kwargs:
            ID = kwargs["ID"]
        elif args:
            ID = args[0]
        else:
            raise Exception("need ID for new Fruit")
        
        # insert self as root stem
        kwargs["stem"] = self
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

    iterate!

    Apple
    Apple
    [0 1 2 3 4 5 6 7 8 9]
    {'color': 'red', 'origin': "Joe's"}
    Apple
    [0 1 2 3 4 5 6 7 8 9]
    Banana
    Banana
    [ 1.00000000e+00  9.80785280e-01  9.23879533e-01  8.31469612e-01
    7.07106781e-01  5.55570233e-01  3.82683432e-01  1.95090322e-01
    6.12323400e-17 -1.95090322e-01 -3.82683432e-01 -5.55570233e-01
    -7.07106781e-01 -8.31469612e-01 -9.23879533e-01 -9.80785280e-01
    -1.00000000e+00 -9.80785280e-01 -9.23879533e-01 -8.31469612e-01
    -7.07106781e-01 -5.55570233e-01 -3.82683432e-01 -1.95090322e-01
    -1.83697020e-16  1.95090322e-01  3.82683432e-01  5.55570233e-01
    7.07106781e-01  8.31469612e-01  9.23879533e-01  9.80785280e-01]
    {'color': 'green', 'origin': "Joe's"}
    Banana
    [ 1.00000000e+00  9.80785280e-01  9.23879533e-01  8.31469612e-01
    7.07106781e-01  5.55570233e-01  3.82683432e-01  1.95090322e-01
    6.12323400e-17 -1.95090322e-01 -3.82683432e-01 -5.55570233e-01
    -7.07106781e-01 -8.31469612e-01 -9.23879533e-01 -9.80785280e-01
    -1.00000000e+00 -9.80785280e-01 -9.23879533e-01 -8.31469612e-01
    -7.07106781e-01 -5.55570233e-01 -3.82683432e-01 -1.95090322e-01
    -1.83697020e-16  1.95090322e-01  3.82683432e-01  5.55570233e-01
    7.07106781e-01  8.31469612e-01  9.23879533e-01  9.80785280e-01]
    
    """
    # # setup 
    import numpy as np
    # root node
    root = Fruit("rottenapple", metadata={"color":"black", "origin": "Joe's"})
    # sprout branches
    x = np.arange(0,10)
    data = x
    root.sprout("Apple", metadata={"color":"red"}, data_x=x, data=data)
    x = np.arange(0,2*np.pi, np.pi/16)
    data = np.cos(x)
    root.sprout("Banana", metadata={"color":"green"}, data_x=x, data=data)
    

    # # testdrive
    
    # class subscriber
    print(root["Apple"])
    # class attributes
    print(root.Apple)

    # class iterator
    print("\niterate!\n")
    for item in root:
        print(item)
        print(item["ID"])
        print(item["data"])
        print(item.get_meta())
        print(item.ID)
        print(item.data)
        


def integritycheck():
    """ better call doctest """
    import doctest
    print("performing doctest test..")
    res=doctest.testmod() # process doctest methods
    print(res)
    print("attempted==succeeded, if no fails\n")


#-#-# module test #-#-#
if __name__ == '__main__': # test if called as executable, not as library
    fruittester()
    #integritycheck()
