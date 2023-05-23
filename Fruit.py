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
    
    def __init__(self, ID=None, stem=None, 
                    data=[], data_x=[], hist=[], hist_bins=[], metadata={},
                        **kwargs):
        super().__init__(**kwargs) # (*args, **kwargs) # superclass inits
        
        self.stem = stem
        self.ID = ID

        self.fruits = []

        self.data = data
        self.data_x = data_x
        self.hist = hist
        self.hist_bins = hist_bins
        self.metadata = metadata

    def __str__(self):
        return self.ID

    def mod(self, dict={}):
        """ hack - to quickly add/mod dict items, aka class variables"""
        self.__dict__.update(dict)

    def sprout(self, *args, **kwargs):
        """make a fruit on this supposed tree"""
        self.fruits.append(Fruit(*args, **kwargs))

    def get_meta(self):
        """ get root's (stem) metadata and update with own """
        if self.stem.metadata:
            meta = self.stem.metadata
        else:
            meta = {}
        meta.update(self.metadata)
        return meta



#-#-# module test #-#-#
if __name__ == '__main__': # test if called as executable, not as library
    
    root = Fruit("rottenapple", metadata={"color":"black", "origin": "Joe's"})

    #Apple = Fruit("Apple",root, metadata={"color":"red"})
    #Bpple = Fruit("Bplle", root, metadata={"color":"green"})
    #root.mod({"fruits":[Apple, Bpple]})
    #print(root.__dict__)

    root.sprout("Apple",root, metadata={"color":"red"})
    root.sprout("Bpple",root, metadata={"color":"green"})

    for fruit in root.__dict__["fruits"]:
        print(fruit.ID)
        print(fruit.get_meta())
