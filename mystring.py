#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mystring - collection of random helper functions, mostly string related

Created on June 21, 2021
@author: thirschbuechler
"""

def dummy(*args, **kwargs):
    pass

def iscontainedin(matchers, listt): # returns matches by modding listt
    return [s for s in listt if any(xs in s for xs in matchers)]


def removecontainingof(tobe_del,listt, sure=0): # removes stuff from listt
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