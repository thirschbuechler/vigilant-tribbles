# -*- coding: utf-8 -*-
"""
Fruitseed.py 

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

import sys, os
import numpy as np
import logging

# import modules if in parent directory via path tmp
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vigilant_tribbles.mailuefterl import bin_to_xaxis

# undo path tmp import
sys.path.pop(len(sys.path)-1)


# # add custom loglevels
def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present 

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    
    https://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility/35804945#35804945
    """
    fine=True
    while(fine):
        if not methodName:
            methodName = levelName.lower()

        if hasattr(logging, levelName):
            #raise AttributeError('{} already defined in logging module'.format(levelName))
            break
        if hasattr(logging, methodName):
            raise AttributeError('{} already defined in logging module'.format(methodName))
        if hasattr(logging.getLoggerClass(), methodName):
            raise AttributeError('{} already defined in logger class'.format(methodName))

        # This method was inspired by the answers to Stack Overflow post
        # http://stackoverflow.com/q/2183233/2988730, especially
        # http://stackoverflow.com/a/13638084/2988730
        def logForLevel(self, message, *args, **kwargs):
            if self.isEnabledFor(levelNum):
                self._log(levelNum, message, args, **kwargs)
        def logToRoot(message, *args, **kwargs):
            logging.log(levelNum, message, *args, **kwargs)

        logging.addLevelName(levelNum, levelName)
        setattr(logging, levelName, levelNum)
        setattr(logging.getLoggerClass(), methodName, logForLevel)
        setattr(logging, methodName, logToRoot)
        fine=False

    
addLoggingLevel('TRAIL',  logging.INFO - 2)
addLoggingLevel('CRUMB', logging.DEBUG + 2)
# levels_now = logging._levelToName.values()
# docu see: def self.setLogLevel()


class Fruit(object):
    #__metaclass__ = GetAttr
    def __init__(self, ID=None, root=None, 
                    data=[],
                    x_axis=None, bins=[],
                    y_axis=None,
                    metadata={},
                    basiclogger = False, loglevel=logging.TRAIL, # logging stuff
                    **kwargs):
        
        # # catch stray kwargs,
        #   as parentclass object doesn't take anything
        if kwargs:
            raise Exception(f"{kwargs=} shouldn't exist here - mis-routed kwargs!")
        super().__init__(**kwargs) # (*args, **kwargs) # superclass inits
        
        # # logger setup
        # basicconfig - ok for small projects
        if basiclogger:
            logging.basicConfig(level=loglevel)
            
            self.log = logging
        
        # Streamhandler - better for a large project with potentially nested ones
        else:
            self.log = logging.getLogger(__class__.__name__)
            
            # prevent console spam by multiple handlers via child-objects
            if not self.log.handlers:
                
                # create console handler and set level to debug
                ch = logging.StreamHandler()
                
                # set level
                ch.setLevel(loglevel)
                
                # create formatter
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                
                # add formatter to ch
                ch.setFormatter(formatter)
                
                # add ch to logger
                self.log.addHandler(ch)

        # legacy hack
        self.myprint = self.log.info

        # # class props etc setup
        self.root = root # root obj
        self.ID = ID # name of this container

        self.fruits = {} # dict of ID:obj of sub-objects

        # every Fruit has metadata
        self.metadata = metadata
        # include root meta
        self.get_meta()
        
        # direct assignment attrs
        self.data = data
        self.bins = bins

        # direct or indirect assignment
        if type(x_axis)!=type(None):
            self.x_axis = x_axis
            if np.any(bins):
                self.log.warning("x_axis and bins given, using x_axis, discarding bins")
        elif np.any(bins):
            # no x_axis (elif), but bins
            self.x_axis = bin_to_xaxis(bins)
        else:
            self.x_axis = [] # eg only contains data=mx

        self.y_axis = y_axis
        # end __init__
        

    def setLogLevel(self, level):
        """ set loglevel for this object

        Levels: 
            * CRITICAL
            * ERROR
            * WARNING
            * INFO
            * *Trail --> debug, shape prints
            * *Crumb --> data prints, print("here") substitute for function debug pos
            * DEBUG --> spammed by matplotlib
            * NOTSET
        """
        self.log.setLevel(level)
    
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
        """ dirty - to experimentally add/mod dict items, aka class methods, variables, .."""
        self.__dict__.update(dict)

    def sprout(self, *args, **kwargs):
        """ spawn a fruit onto this object,
            be it a tree (no parent root),
            or another fruit

            also return new obj, for convenience
            """
        if "ID" in kwargs:
            ID = kwargs["ID"]
        elif args:
            ID = args[0]
        else:
            raise Exception("need ID for new Fruit")
        
        # insert self as root
        kwargs["root"] = self
        # make fruit
        new = Fruit(*args, **kwargs)
        # auto inherit all metadata
        new.metadata = new.get_meta()
        # put into meta-dict
        self.fruits.update({ID:new})
        # also make it an attribute
        self.__dict__.update(self.fruits)

        return new


    def slicer(self, slice=None):
        """ sprout a slice of data, datax of slice,
            FruitID = str(slice)

            also return obj, for convenience
            """
        if slice:
            data = self.data[slice[0]:slice[1]]
            x_axis = self.x_axis[slice[0]:slice[1]]
            return self.sprout(str(slice), data=data, x_axis=x_axis, y_axis=self.y_axis)
        else:
            return self


    def get_meta(self):
        """ get root's metadata and update with own """
        if self.root:
            if self.root.metadata:
                meta = self.root.metadata
            else:
                meta = {}
        else:
            meta = {}
        meta.update(self.metadata)
        return meta


def fruittester():
    """
    note: py3.10.6 has blankline-html tags and indented list-plotting
    >>> fruittester()
    Apple
    Apple
    <BLANKLINE>
    iterate!
    <BLANKLINE>
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
    root.sprout("Apple", metadata={"color":"red"}, x_axis=x, data=data)
    x = np.arange(0,2*np.pi, np.pi/16)
    data = np.cos(x)
    root.sprout("Banana", metadata={"color":"green"}, x_axis=x, data=data)
    

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
        

def slice_test():
    """
    >>> slice_test()
    [3, 4]
    [8, 9]
    """
    root = Fruit("rottenapple", metadata={"color":"black", "origin": "Joe's"}, x_axis=[1,2,3,4,5], data=[6,7,8,9,10])
    slice = [2,4]
    
    ele = root.slicer(slice=slice)
    # access directly or via dict of main
    print(ele.x_axis)
    print(root[str(slice)].data)
    # check meta
    print(ele.metadata)

def integritycheck():
    """ better call doctest """
    import doctest
    print(f"doctest called in ({__file__})")
    res=doctest.testmod() # process doctest methods
    print(res)
    print("attempted==succeeded, if no fails\n")


#-#-# module test #-#-#
if __name__ == '__main__': # test if called as executable, not as library
    #fruittester()
    slice_test()
    integritycheck()
