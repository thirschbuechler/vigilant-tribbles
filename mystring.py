#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mystring - collection of random helper functions, mostly string related


note: listt is used to not overwrite builtin list fct

Created on June 21, 2021
@author: thirschbuechler
"""
import re #sorting
from matplotlib.ticker import EngFormatter # enginerd
#import numpy as np # ndarray for list vecorization in split string index bla


def dummy(*args, **kwargs):
    """ function pointer to nowhere (and eat any arguments)"""
    pass


def find_all(query, string):
    """ get all occourences of substring in strin"""
    return [m.start() for m in re.finditer(query, string)]


def str_to_blocktext(input, in_sep, out_sep=" ", maxlen=5):
    """ turns string separated by delimiters into newline-separated str of max(maxlen;maxlen_line)
    out_sep != in_sep
    
    >>> str_to_blocktext("this, is, very, long, this, is, even, longer, so, to, speak", in_sep=", ", maxlen=10)
    'this is very\\nlong this\\nis even\\nlonger\\nso to speak\\n\\n'
    """
    items = input.split(in_sep)

    if out_sep == in_sep:
        raise Exception(f"str_to_blocktext won't work for {out_sep=}=={in_sep=}")

    lines = []
    i=0

    def fetch_if_possible(i, items):
        if i <= len(items)-1:
            o = items[i]
            #items.pop(i)
            return o
        else:
            return ""

    while len(items)>0:
        line = ""
        item = []
        while len(line)+len(item)<maxlen:
            item = fetch_if_possible(i, items)
            if line:
                line = f"{line}{out_sep}{item}"
            else: # omit sep for first
                line = f"{line}{item}"
            if item=="":
                break
            i+=1
        # then, terminate
        line+="\n"
        #i+=1
        lines.append(line)
        if item=="":
            break

    return "".join(lines)


def dict_to_str(mydict):
    """ turn dictionary into human readable string
        note: even nicer would be print(pd.DataFrame([mydict]))
    
    >>> dict_to_str({"a":10, "b":20})
    'a: 10, b: 20'
    >>> str({"a":10, "b":20})
    "{'a': 10, 'b': 20}"
    """
    st = str(mydict)
    st=removestringparts(["\"", "'", "{", "}"], [st])
    st="".join(st)

    return st


def list_to_str(mydict):
    """ turn dictionary into human readable string
    
    >>> dict_to_str({"a":10, "b":20})
    'a: 10, b: 20'
    >>> str({"a":10, "b":20})
    "{'a': 10, 'b': 20}"
    """
    st = str(mydict)
    st=removestringparts(["\"", "'", "[", "]"], [st])
    st="".join(st)

    return st


def dictlist_intersection(mydictlist):
    """
    find common key-value pairs in a list of dictionaries
    (as "dict1 & dict2" doesn't work)
    
    doesn't like if more than 1 sub-dict has a list!

    dccsillag: https://stackoverflow.com/questions/18554012/intersecting-two-dictionaries

    >>> dictlist_intersection([{"a":3, "b":4, "d":0},{"a":1, "c":4, "d":0},{"d":0, "a":4, "x":0}])
    {'d': 0}
    >>> dictlist_intersection([{"a":3, "b":4, "nestedlist":[1,2,3,"aa"]},{"a":1, "c":4, "d":0},{"d":0, "a":4, "x":0}])
    {}

    #>>> dictlist_intersection([{"a":3, "b":4, "nestedlist":[1,2,3,"aa"]},{"a":1, "c":4, "nestedlist":[1,2,3,"aa"]}])
    #   TypeError: unhashable type: 'list
    """
    if not (type(mydictlist[0]) == dict):
        raise Exception("not a dict as list element")
    
    for i, item in enumerate(mydictlist):
        if i==0:
            # initialize
            commons = item
        else:
            # intersect with last one
            commons = dict(commons.items() & item.items()) # dict.items() produces keys+values
    return commons


def dict_a_fully_in_b(dict_a={}, dict_b={}):
    """ is dict_a fully contained in dict_b?

    
    >>> dict_a_fully_in_b({1:2, 2:3}, {1:2, 2:3})
    True

    >>> dict_a_fully_in_b({1:3, 2:3}, {1:2, 2:3})
    False

    >>> dict_a_fully_in_b({1:2, 2:3}, {1:2, 2:3, 3:4})
    True

    >>> dict_a_fully_in_b({1:2}, {1:3, 2:3})
    False

        
    """
    return (len(dictlist_intersection([dict_b, dict_a]))==len(dict_a))



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
        - for substrings use:
            - "if substring in string", see ['.', 'b', 'i', 'n']
            - or pack both into lists

        >>> iscontainedin(".",["abc","dev.f"])
        ['dev.f']
        >>> iscontainedin("a.",["abc","dev.f"])
        ['abc', 'dev.f']
        >>> iscontainedin(["a."],["abc","dev.f"])
        []
        >>> iscontainedin([".d"],["abc","dev.f"])
        []
        >>> iscontainedin(["dev"],["abc","dev.f"])
        ['dev.f']
        >>> iscontainedin(".","dev.f")
        ['.']
        >>> iscontainedin(".bin","C:\\bla.bin")
        ['.', 'b', 'i', 'n']
        >>> iscontainedin([".bin"],["C:\\bla.bin"])
        ['C:\x08la.bin']
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


def replacestringparts(matchers, listt, newstr=""): 
    """returns list of input listt (list) with replaced matchers (list) by one newstr
    """
    if type(matchers)==str:
        matchers=[matchers] # assume if a string given to only replace the whole thing
    
    for matcher in matchers:
        listt = [line.replace(matcher,newstr) for line in listt]  # replace with newstr
    return listt

def removestringparts(matchers, listt): 
    """returns cleaned list of input listt (list) and to-be-removed matchers (list)
    
    >>> removestringparts("QQ",["QQasdf","asdfQQasdf"])
    ['asdf', 'asdfasdf']
    
    >>> removestringparts(["QQ","s"],["QQasdf","asdfQQasdf"])
    ['adf', 'adfadf']
    """
    return replacestringparts(matchers, listt, "")

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


def enginerd(value, unit='', places=2, sep="\N{THIN SPACE}", **kwargs): #u2009 thinspace not nice in tex, also "G" in graph and Hz in label == unprofessional -_-
    """ return engineer-nerd formatted string for a given float
        optional:
        - places : how many decimals (default = 2)
        - unit (str t append)
        - sep: separator (str, default Unicode-thin-space, non-ascii!)

        # https://matplotlib.org/3.1.0/gallery/text_labels_and_annotations/engineering_formatter.html
        
        name is pun on engineer-nerd
    """
    return(EngFormatter(places=places, sep=sep, **kwargs).format_eng(value)+unit)


###################### testing #############################
def integritycheck():
    """ better call doctest """
    import doctest
    print(f"doctest called in ({__file__})")
    res=doctest.testmod() # process doctest methods
    print(res)
    print("attempted==succeeded, if no fails\n")



#-#-# module test #-#-#
if __name__ == '__main__': # test if called as executable, not as library            
    integritycheck()

