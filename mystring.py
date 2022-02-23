#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# %%
"""
Mystring - collection of random helper functions, mostly string related


note: listt is used to not overwrite builtin list fct

Created on June 21, 2021
@author: thirschbuechler
"""
import re #sorting
#import numpy as np # ndarray for list vecorization in split string index bla


def dummy(*args, **kwargs):
    """ function pointer to nowhere (and eat any arguments)"""
    pass


#https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    """ alist.sort(key=natural_keys) sorts in human order

    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def sort_human(stuff):
    """  sort ascending if multi-digit numbers appera, etc.
    >>> sort_human(["bla_16","bla_6"])
    ['bla_6', 'bla_16']
    """
    stuff.sort(key=natural_keys)
    return stuff


def iscontainedin(matchers, listt):
    """ returns matches of listt element 
        - listt can be list
        - listt can also be a str, see 2nd test
        - for substrings use: "if substring in string", see weird 3rd output

        >>> iscontainedin(".",["abc","dev.f"])
        ['dev.f']
        >>> iscontainedin(".","dev.f")
        ['.']
        >>> iscontainedin(".bin","C:\\bla.bin")
        ['.', 'b', 'i', 'n']
        >>> iscontainedin(".bin","C:\\bla")
        []
    """
    return [s for s in listt if any(xs in s for xs in matchers)]


#https://stackoverflow.com/questions/7852384/finding-multiple-common-starting-strings
def groupByPrefix(strings,delimiter="_"):
    """ make (keyed) dict of list up to delimiter 
    
    >>> groupByPrefix(["run0_0","run0_1","run1_bla"])
    {'run0': ['0', '1'], 'run1': ['bla']}
    """
    stringsByPrefix = {}
    for string in strings:
            prefix, suffix = map(str.strip, string.split(delimiter, 1))
            group = stringsByPrefix.setdefault(prefix, [])
            group.append(suffix)
    return stringsByPrefix


def removecontainingof(tobe_del,listt, sure=0):
    """ removes stuff from original list, NO return val """
    
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


# $ToDo - this naming scheme would be way nicer.. 
def rm_str_parts_list(matchers, listt): 
    return removestringparts(matchers, listt)


#https://stackoverflow.com/questions/45104747/split-python-string-by-predifned-indices
def str_split_via_indices(s="",split_points=[]):
    """
    split a string via a list of indices
    - s: inputstring
    - split_points: indices where to split
    >>> str_split_via_indices(s="thequickbrownfoxjumpsoverthelazydog",split_points=[3, 8, 13, 16, 21, 25, 28, 32])
    ['the', 'quick', 'brown', 'fox', 'jumps', 'over', 'the', 'lazy', 'dog']"""

    # insert first and last boundary
    #split_points=np.array(split_points)#vectorize compatiblity
    split_points.insert(0,0)
    split_points.append(len(s))
    #split_points = [0,*split_points, len(s)]
    # stackoverflow magic
    return([s[i: j] for i, j in zip(split_points, split_points[1:])])


###################### testing #############################
def integritycheck():
    """ better call doctest """
    import doctest
    print("performing doctest test..")
    res=doctest.testmod() # process doctest methods
    print(res)
    print("attempted==succeeded, if no fails\n")



#-#-# module test #-#-#
if __name__ == '__main__': # test if called as executable, not as library            
    integritycheck()
# %%
