
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mailüfterl

general computation fcts

- common math
- nan handling
- little statistics

Created on Fri Mar 11 19:06:42 2022
@author: thirschbuechler
"""
import colored_traceback.always # colorize terminal output and errors in terminal and vscode terminal
import numpy as np
import pandas as pd
import warnings # numpy nanzero zeroslice stuff


def dummy(*args,**kwargs):
    pass # NOP - do nothing


# define lookup dir for eval fct
eval_fct_str_dict={"np.min":np.min, "np.avg":np.average, "np.max":np.max}
eval_str_fct_dict={np.min:"np.min", np.average:"np.avg", np.max:"np.max"}



def sample_var(*args, **kwargs):
    """ sample variance
        "provides an unbiased estimator of the variance of a hypothetical infinite population"

        be careful with multidim, "axis" kwarg might help

    # [1,5], mean=6, n=2, (2²+2²)/(n-1)=8
    >>> sample_var([1,5])
    8.0

    """
    kwargs["ddof"]=1
    return np.nanvar(*args, **kwargs)


def bin_to_xaxis(bin_edges):
    """
    takes a histo bin_edges array and returns the corresponding x-axis (bin_centers)
    
    >>> bin_to_xaxis([0,1,2])
    [0.5, 1.5]
    
    >>> bin_to_xaxis([0,1,2,3,4])
    [0.5, 1.5, 2.5, 3.5]
    """
    bin_centers = [bin_edges[i]+(bin_edges[i+1]-bin_edges[i])/2 for i in range(0,len(bin_edges)-1)]
    return bin_centers


def xaxis_to_bins(xaxis):
    """ turn a x-axis into bins, inversion of bins_to_xaxis
    
    >>> xaxis_to_bins(bin_to_xaxis([0,1,2,3,4]))
    [0.0, 1.0, 2.0, 3.0, 4.0]
    
    >>> xaxis_to_bins(bin_to_xaxis([0,1,2]))
    [0.0, 1.0, 2.0]
    """
    # calc edges
    left_edges = [xaxis[i]-(xaxis[i+1]-xaxis[i])/2 for i in range(0,len(xaxis)-1)]
    right_edges = [xaxis[i+1]+(xaxis[i+1]-xaxis[i])/2 for i in range(0,len(xaxis)-1)]

    # add almost rightest edge to results
    if len(xaxis) > 2:
        # general case
        left_edges.append(right_edges[-2])
    else:
        # special case
        left_edges.append(xaxis[0]+(xaxis[1]-xaxis[0])/2)
    
    # general - add rightest edge to results
    left_edges.append(right_edges[-1])
    # return results
    return left_edges


def count_non_nan(data):
    """ count non_nan in numpy array
    
    CAUTION: cannot handle np.array([np.array, np.array])
            --> use np.concatenate with transposed arr, etc.
    """
    #print(type(data))
    #print(f"{data=}")
    return np.count_nonzero(~np.isnan(data))


def count_nan(data):
    """ count nan values in numpy array / matrix """
    b = np.isnan(data)
    return len(b[b==True])


def auto_round(x):
    """
    round to significance

    >>> auto_round(15000)
    15000
    >>> auto_round(15555)
    16000
    >>> auto_round(153)
    150
    """
    r = int (np.log10(x)) - 1
    return (round(x, -r))


def auto_floor(x):
    """
    round down to significance

    >>> auto_floor(15000)
    15000
    >>> auto_floor(15555)
    15000
    >>> auto_floor(153)
    150
    """
    r =  int (np.log10(x)) - 1
    if r>0:
        expo = np.power(10,r)
        x = np.floor(x/expo)*expo
    else:
        # avoid ValueError: Integers to negative integer powers are not allowed.
        pass # don't change anything
    return int(x)


def auto_ceil(x):
    """
    round up to significance

    >>> auto_ceil(15000)
    15000
    >>> auto_ceil(15555)
    16000
    >>> auto_ceil(153)
    160
    """
    r =  int (np.log10(x)) - 1
    if r>0:
        expo = np.power(10,r)
        x = np.ceil(x/expo)*expo
    else:
        # avoid ValueError: Integers to negative integer powers are not allowed.
        pass # don't change anything
    return int(x)


def histo_weighter(**kwargs):
    """ common histo weighter for myink and mailüfterl"""
    ## read in
    x = kwargs["x"]

    #local kwargs - defaults
    lk_def = {"percent":False, "autorange":False, "basearray": None}
    lk = {"percent":False, "autorange":False, "basearray": None}
    # update lk with new vals, without taking other kwarg keys
    #lk.update((k, kwargs[k]) for k in set(kwargs).intersection(lk)) # doesnt work
    lk.update(kwargs) # also reads new keys

    ## eval logic
    # autorange
    if lk["autorange"]:
        myrange = (nanmin(x), nanmax(x))
        #if not np.any(myrange):
        #    raise Exception(f"data autorange empty! - reported by ml.histogram.hosto_weighter.autorange\n{x=}")
        kwargs["range"] = myrange

    # percent
    if lk["percent"]:
        # which percentbase
        if type(lk["basearray"]) != type(None):
            if not len(lk["basearray"]): # if len 0
                basearray = x
            else:
                basearray = lk["basearray"]
                #pass
        else: # if no basearray
            basearray = x
        #basearray = np.array(basearray)
        lk["weights"]=np.ones(np.shape(x)) / count_non_nan(basearray)
        kwargs["weights"]=lk["weights"]

    # remove processed keys, return
    for key in list(lk_def.keys()):
        kwargs.pop(key, "")
    return kwargs


def histogram(**kwargs):
    """ weighted histograms
        - x (arr): data
        - autorange (bool): range=[nanmin(x), nanmax(x)]
        - percent (bool): weigh to reflect percent
        - basearray (arr): use countnonnan(basearray) as percent base

        BE CAUTIOUS OF np.nan in weights! no-output, even for many non-zero weights can happen
    """

    # process args, delete non-hist kwargs
    x = kwargs["x"]
    #if not np.any(x): # fail silent for now, not necessarily a problem
    #    raise Exception("data empty! - reported by ml.histogram")
    kwargs = histo_weighter(**kwargs)
    kwargs.pop("x")


    # numpy hist, forward hist kwargs
    n, bins = np.histogram(a=x,**kwargs)

    return n,bins
    """
    attention: 
    default parameter in np.histogram is "a"
        numpy histogram ignores weights, so re-do n afterwards
    default parameter in matplotlib.hist is "x"
        mpl hist works with weights as expected
    """


def is_odd(num):
    return num & 0x1


#https://www.appsloveworld.com/numpy/100/89/in-numpy-how-to-detect-whether-an-argument-is-a-ragged-nested-sequences
def is_scalar(a):
    if np.isscalar(a):
        return True
    try:
        len(a)
    except TypeError:
        return True
    return False

def get_shape(a):
    """
    Returns the shape of `a`, if `a` has a regular array-like shape.

    Otherwise returns None.
    """
    if is_scalar(a):
        return ()
    shapes = [get_shape(item) for item in a]
    if len(shapes) == 0:
        return (0,)
    if any([shape is None for shape in shapes]):
        return None
    if not all([shapes[0] == shape for shape in shapes[1:]]):
        return None
    return (len(shapes),) + shapes[0]

# thanks copilot
def is_iterable(item):
    try:
        iter(item)
        return not isinstance(item, str)  # Exclude strings
    except TypeError:
        return False

# thanks copilot
def is_ragged(a):
    if isinstance(a, np.ndarray) and a.dtype != object:
        # If a is a non-object numpy array, it's not ragged
        return False
    if isinstance(a, list):
        # If a is a list, check if all elements have the same length
        # Use is_iterable to avoid TypeError on non-iterable elements
        lengths = [len(item) if is_iterable(item) else 0 for item in a]
        return len(set(lengths)) > 1
    if isinstance(a, np.ndarray):
        # If a is an object numpy array, check if all elements have the same shape
        # Use is_iterable to avoid TypeError on non-iterable elements
        shapes = [np.shape(item) if is_iterable(item) else (0,) for item in a]
        return len(set(shapes)) > 1
    # If a is not a list or array, it's not ragged
    return False

def integritycheck():
    """ better call doctest """
    import doctest
    print(f"doctest called in ({__file__})")
    # process doctest methods
    #res = doctest.testmod(optionflags=doctest.REPORT_UDIFF) # traceback short  - default anyway
    res = doctest.testmod()

    print(res)
    print("attempted==succeeded, if no fails\n")


def babysit(eval, *args, **kwargs):
    """ numpy nan-operation silencer
        (but its better use pandas for ragged arrays w. skipna=True per default)
    
        nan-matrices shall be allowed to have means over nans or zeros without giving a warning,
        expect to see RuntimeWarnings otherwise

        note: all runtime warnings of one fct ignored
        maybe to do only ignore zeromean nan slice ones

        also make sure to return nan if no valid data is present, e.g. all nans in a slice
        (as the default numpy behaviour is weird)
    """

    # this can return an element for parsing a ragged-list with nans instead of having an empty element there
    return_nan = kwargs.pop("return_nan", False)
    if not my_any(args) and return_nan:
        return np.nan
    else:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            return eval(*args,**kwargs)
        
        # alternatively (even thouth with_context is superior):
        # np.seterr(divide='ignore', invalid='ignore') # temp disable for nan operations
        # nan operations
        # np.seterr(divide='warn', invalid='warn') # re-enable
            

# some hairy cases are at bottom in "main", with scalar and/or nested elements    
def nanmean(*args, **kwargs):
    """ nanmean with babysit - no RuntimeWarning for nans
        - return_nan (bool)- option if no valid data is present"""  
    return babysit(np.nanmean,*args, **kwargs)

def nanmedian(*args, **kwargs):
    """ nanmean with babysit - no RuntimeWarning for nans
        - return_nan (bool)- option if no valid data is present"""  
    return babysit(np.nanmedian,*args, **kwargs)

def nanmax(*args, **kwargs):
    """ nanmax with babysit - no RuntimeWarning for nans
        - return_nan (bool)- option if no valid data is present"""
    return babysit(np.nanmax,*args, **kwargs)

def nanmin(*args, **kwargs):
    """ nanmin with babysit - no RuntimeWarning for nans
        - return_nan (bool)- option if no valid data is present"""
    return babysit(np.nanmin,*args, **kwargs)

def nanstd(*args, **kwargs):
    """ nanstd with babysit - no RuntimeWarning for nans
        - return_nan (bool)- option if no valid data is present"""
    return babysit(np.nanstd,*args, **kwargs)

def divide(*args, **kwargs):
    """ divide with babysit - no RuntimeWarning for nans
        - return_nan (bool)- option if no valid data is present"""
    return babysit(np.divide,*args, **kwargs)


def LSQ_line(x, y):
    """ THE OLD FASHIONED MOORE PENROSE WAY"""
    # make pinv basis
    A = np.vstack([x, np.ones(len(x))]).T
    # make pinv and unpack
    k, d = np.linalg.lstsq(A, y, rcond=None)[0]
    
    return k,d


def sign_sym(var):
    """ return plus/minus sign of number

        input: scalar number
        output: char (+/-/?)
    
    >>> sign_sym(3)
    '+'
    >>> sign_sym(-10)
    '-'
    >>> sign_sym(np.nan)
    '?'
    >>> sign_sym("b")
    '?'
    """
    # filter bs
    if type(var) == str:
        return "?"
    if np.isnan(var):
        return "?"
    # otherwise, return sign char
    # (numpy's sign returns +-1 number)
    else:
        return (f'{var:+g}')[0]


def ragged_nan_to_val(rag, val, copy=True):
    """
    cycle over ragged list an replace nans with a value
    - rag (input)
    - value (to find)
    - copy: output array new memory? (def: true)

    returns modded rag

    >>> ragged_nan_to_val(rag=np.array([[1,2,3], [0,np.nan]], dtype=object), val=0)
    array([array([1, 2, 3]), array([0., 0.])], dtype=object)
    >>> ragged_nan_to_val(rag=np.array([np.array([1,2,3]), np.array([0,np.nan])], dtype=object), val=0)
    array([array([1, 2, 3]), array([0., 0.])], dtype=object)
    """
    if copy:
        x = rag.copy()
    else:
        x=rag

    # for symmetry for ragged_val_to_nan:
    # convert potential lists to arrays,
    # also fixes "TypeError: only integer scalar arrays can be converted to a scalar index"
    x = np.array([np.array(xi) for xi in x], dtype=object)

    for xi in x:
        xi[np.isnan(xi)] = val

    return x

def ragged_val_to_nan(rag, val, copy=True, new_dtype=None):
    """
    cycle over ragged list and replace value with nans
    - rag (input)
    - value (to replace)
    - copy: output array new memory? (def: true)
    - new_dtype: choose np.float16/32/64, if issues
    
    returns modded rag

    >>> ragged_val_to_nan(rag=np.array([[1,2,3], [0,np.nan]], dtype=object), val=0, new_dtype=np.float16)
    array([array([1., 2., 3.], dtype=float16),
           array([nan, nan], dtype=float16)], dtype=object)
    >>> ragged_val_to_nan(rag=np.array([np.array([1,2,3]), np.array([0,np.nan])], dtype=object), val=0, new_dtype=np.float16)
    array([array([1., 2., 3.], dtype=float16),
           array([nan, nan], dtype=float16)], dtype=object)

    """
    if copy:
        x = rag.copy()
    else:
        x=rag

    if new_dtype:
        x = np.array([np.array(xi, dtype=new_dtype) for xi in x], dtype=object)
    else:
        # just convert potential lists to arrays
        x = np.array([np.array(xi) for xi in x], dtype=object)

    for xi in x:
        xi[xi == val] = np.nan

    return x


def mx_diag_mirror(X):
    # https://stackoverflow.com/questions/16444930/copy-upper-triangle-to-lower-triangle-in-a-python-matrix/42209263
    X = np.triu(X) #remove NANs of lower triag, which were used to hide redundancy
    return X + X.T - np.diag(np.diag(X))
    

def singledim_mod_testdata(i):
    if i==0:
        data = np.array([[1,2],[3,4]])
        data = [data,data]
        data = [data,data]
        return data

    elif i==1:
        return [np.array([ 17,  14,  10,  47, 171,  44, 105,  91,  88,  14])]
    
    elif i==0.5:
        return np.array([1,2,3,4,5])
    
    elif i==2:
        return np.array([[[1,2],[3,4]],[[5,6],[7,8]]])
    
    elif i==3:
        return np.array([([[[1,2],[3,4]],[[5,6],[7,8]]])], dtype=object)

def singledim_mod(data):
    """ takes multidimensional array and flattens all but first one - useful for boxplot(), etc.
        aka dimred, dimension reduction, ...
        --> only keep first dimension
        
        BETTER: roadkill (below)

    # doctest - show contents of singledim_mod_testdata and then apply to function
    >>> np.shape(singledim_mod_testdata(0))
    (2, 2, 2, 2)
    >>> np.shape(singledim_mod(singledim_mod_testdata(0)))
    (2, 8)
    >>> np.shape(singledim_mod_testdata(1))
    (1, 10)
    >>> np.shape(singledim_mod(singledim_mod_testdata(1)))
    (1, 10)

    >>> np.shape(singledim_mod_testdata(3))
    (1, 2, 2, 2)
    >>> np.shape(singledim_mod(singledim_mod_testdata(3)))
    (1, 8)

    """
    args = []
    args = np.shape(data)
    data = np.reshape(data, newshape=(int(args[0]), int(np.prod(args[1:]))))

    return data

def recursive_array(obj):
    # base case: if obj is not a list or a series, return it as a numpy array
    if not isinstance(obj, (list, pd.Series)):
        return np.array(obj)
    # recursive case: if obj is a list or a series, apply recursive_array to each element and stack them
    else:
        return np.stack([recursive_array(x) for x in obj])
    

def roadkill(thing, hard=False, soft=False):
    """Flatten if possible - remove any dimensions and make a list.
    
    Args:
        *thing: The object to flatten.
        * hard (bool, optional): Determines the level of "hardness". Defaults to False.
            - False: please be flat - squish a little
            - True: sudo "be_flat!" - deploy the hammer
            - 2: sneaky "be_flat!" - add a dummy (and remove it again)
        * soft (bool, optional): Determines the level of "softness". Defaults to False.
            - False: no softness, hardness possible
            - True: np.squeeze, disable hard

    Returns:
        The flattened object.

    (Pylance Linter)

    
    >>> np.shape(singledim_mod_testdata(0))
    (2, 2, 2, 2)
    >>> np.shape(roadkill(singledim_mod_testdata(0)))
    (16,)
    
    >>> np.shape(singledim_mod_testdata(1))
    (1, 10)
    >>> np.shape(roadkill(singledim_mod_testdata(1)))
    (10,)
    
    >>> np.shape(singledim_mod_testdata(0.5))
    (5,)
    >>> np.shape(roadkill(singledim_mod_testdata(0.5)))
    (5,)
    
    >>> np.shape(roadkill(singledim_mod_testdata(0.5), hard=True))
    Traceback (most recent call last):
    ValueError: zero-dimensional arrays cannot be concatenated
    >>> np.shape(roadkill(singledim_mod_testdata(0.5), hard=2))
    (10,)
    
    >>> np.shape(roadkill(singledim_mod_testdata(0), hard=2))
    (32,)
    
    >>> np.shape(singledim_mod_testdata(2))
    (2, 2, 2)
    >>> np.shape(roadkill(singledim_mod_testdata(2), soft=True))
    (2, 2, 2)
    >>> np.shape(roadkill(singledim_mod_testdata(2), hard=0))
    (8,)
    >>> np.shape(roadkill(singledim_mod_testdata(2), hard=1))
    (8,)
    >>> np.shape(roadkill(singledim_mod_testdata(2), hard=2))
    (16,)


    >>> np.shape(singledim_mod_testdata(3))
    (1, 2, 2, 2)
    >>> np.shape(roadkill(singledim_mod_testdata(3), soft=True))
    (2, 2, 2)
    >>> np.shape(roadkill(singledim_mod_testdata(3), hard=0))
    (8,)
    >>> np.shape(roadkill(singledim_mod_testdata(3), hard=1))
    (8,)
    >>> np.shape(roadkill(singledim_mod_testdata(3), hard=2))
    (16,)


    """
    if not (type(thing) == type(np.array([1]))):
            thing = np.array(thing, dtype="object")
    if np.shape(thing) == np.shape(1): # numpy shape returns warning ragged nested sequences, unless dtype=obj 
        return thing # no dimension
    elif (hasattr(thing, "__iter__")):
        
        # convert in case boolean is used
        hard = int(hard)
        
        if soft:
            # skip hardnesses
            return np.squeeze(thing)

        # please be flat - squish a little
        if not hard:
            return(thing.flatten()) 
        
        # sudo "be_flat!" - deploy the hammer
        elif hard==1:
            # - join np.arrays in list via conc
            # - then join lists via ravel)
            return(np.concatenate(thing).ravel())
        
        # sneaky "be_flat!" - add dummy NANs on end - doesn't matter in some cases
        elif hard==2:
            # - join np.arrays in list via conc
            # - then join lists via ravel)
            # - add a dummy dimension, so it also works with single-dimension arrays
            a = []
            #a = np.array([[] for ele in range(0,len(np.shape(thing)))])
            thing = recursive_array(thing)
            a = np.full(shape=np.shape(thing),fill_value=np.nan)
            return(np.concatenate(np.array([thing,a], dtype="object")).ravel())
            

    else:
        return thing


def tuple_concat(*args):
    """ input two tuples with same dimension to concatenate

    # # unpacking examples # #

    # iterate over (packed) tuple-columns
    for a,b,c in data:
        print(a,b,c)

    # unpack tuple-columns
    a,b,c = data.T
        print(b[4])

    # loop over unpacked columns via packing
    for a,b,c in zip(a,b,c):
        print(a,b,c)

    # unpack and re-pack for looping, just because :P
    for a,b,c in zip(*data.T):
        print(a,b,c)

    >>> a = list(range(0,3))
    >>> b = ["a", "b", "c"]
    >>> c = [0.0, 1.1, 3.3]
    >>> tuple1 = a,b,c
    >>> a = list(range(0,3))
    >>> b = ["d", "e", "f"]
    >>> c = [5.0, 6.6, 3.3]
    >>> tuple2 = a,b,c
    >>> x = tuple_concat(tuple1, tuple2)    
    >>> x[3]
    array([0, 'd', 5.0], dtype=object)
    """
    # unpack tuples
    if len(args) >1:
        tuples = args
    else:
        tuples = args[0]

    # convert to concatenable and orient
    tuples = [np.array(ti, dtype=object).T for ti in tuples]
    
    # concatenate into matrix
    return np.concatenate(tuples)


#https://stackoverflow.com/questions/51960857/how-can-i-get-a-list-shape-without-using-numpy
from collections.abc import Sequence, Iterator
from itertools import tee, chain

def is_shape_consistent(lst: Iterator):
    """
    check if all the elements of a nested list have the same
    shape.

    first check the 'top level' of the given lst, then flatten
    it by one level and recursively check that.

    :param lst:
    :return:
    """

    lst0, lst1 = tee(lst, 2)

    try:
        item0 = next(lst0)
    except StopIteration:
        return True
    is_seq = isinstance(item0, Sequence)

    if not all(is_seq == isinstance(item, Sequence) for item in lst0):
        return False

    if not is_seq:
        return True

    return is_shape_consistent(chain(*lst1))

def get_shape(lst, shape=()):
    """
    returns the shape of nested lists similarly to numpy's shape.

    :param lst: the nested list
    :param shape: the shape up to the current recursion depth
    :return: the shape including the current depth
            (finally this will be the full depth)
    """

    if not isinstance(lst, Sequence):
        # base case
        return shape

    # peek ahead and assure all lists in the next depth
    # have the same length
    if isinstance(lst[0], Sequence):
        l = len(lst[0])
        if not all(len(item) == l for item in lst):
            msg = 'not all lists have the same length'
            raise ValueError(msg)

    shape += (len(lst), )
    
    # recurse
    shape = get_shape(lst[0], shape)

    return shape


def my_any(thing):
    """
    
    # a.any(thing) warning fix, for evaluating bool(list([1,2,3])) or bool(list([0,0,0])), bool(list([[],[],[]])) etc.
    # np.size(thing)>0: # np.size(y_axis)): # bool-list cast is alternative to a.any()

    # # empty # #
    # none
    >>> my_any(None)
    False

    # empty list
    >>> my_any([])
    False

    # empty dict
    >>> my_any({})
    False

    # empty array
    >>> my_any(np.array([]))
    False

    # empty matrix array
    >>> my_any(np.array([[], []]))
    False



    # # full # #

    # nan - not a feature but it is what it is
    # use sth like "my_any(item) and count_non_nan(item)"
    >>> my_any(np.nan)
    True

    # str
    >>> my_any("bla")
    True

    # int
    >>> my_any(3)
    True

    # float
    >>> my_any(123.456)
    True

    # str dict
    >>> my_any({"key1":"value1"})
    True

    # mixed dict
    >>> my_any({"key1":"value1", "key2":2, "key3": [], "key4": [1,2,3]})
    True

    # str list
    >>> my_any(["12", "34"])
    True

    # float list
    >>> my_any([12.34, 56.78])
    True
    
    # array
    >>> my_any(np.array([12.34, 56.78]))
    True

    # empty matrix array
    >>> my_any(np.array([[12.34, 56.78], [12.34, 56.78]]))
    True

    """

    return bool(np.any(np.array(thing, dtype=object)))


def bintreesearch(evalfct, maxdeviate, left, right, echo=False, aborter=None):
    """ find the acceptable maxdeviate on a monotonic fct in a given interval [left, right]
    
    # trivial test - find y close to 0.5 on slope y=x-0.1 from x 0.5 to 1.5
    >>> bintreesearch(evalfct=(lambda x: x-0.1), maxdeviate=0.5, left=0.5, right=1.5 )
    0.5625

    # failure mode test - cannot reach value outside bounds
    >>> bintreesearch(evalfct=(lambda x: x-0.1), maxdeviate=0.2, left=0.5, right=1.5 )
    Traceback (most recent call last):
    Exception: no convergence, evals are same 0.4 with maxdeviate=0.2
    """
    # fence edges: left, center, right
    center = (left+right)/2

    # check for failure
    if left == right:
        raise Exception(f"no convergence, left==right=={left} with {maxdeviate=}")

    # paths inbetween
    leftpath = (left+center)/2
    rightpath = (right+center)/2

    # evaluate
    testvalues = [leftpath, rightpath]
    evals = [evalfct(item) for item in testvalues]

    # check for failure
    if evals[0] == evals[1]:
        raise Exception(f"no convergence, evals are same {evals[0]} with {maxdeviate=}")

    # check further abort condition if given
    if aborter:
        aborter(evals)

    # find minimum valid value of both
    min_dev_res = np.nanmin(evals)

    # is it left or right?
    minpos = evals.index(min_dev_res)

    # input val to achieve min
    argmin = testvalues[minpos]
    
    # echo
    if echo:
        print(f"inputs {left}{right} caused {evals}")

    # return if found
    if min_dev_res <= maxdeviate:
        return argmin
    # or go on
    # (till RecursionError or left==right Exception above)
    else:
        if minpos < 1:
            return bintreesearch(evalfct=evalfct, maxdeviate=maxdeviate, left=left, right=center, echo=echo)
        else:
            return bintreesearch(evalfct=evalfct, maxdeviate=maxdeviate, left=center, right=right, echo=echo)


def list_to_range(lst):
    low = int(min(lst))
    high = int(max(lst))

    if lst == list(range(low, high+1)):
        return range(low, high+1)
    else:
        return lst
    
    
'''
def availability(data, thresh=-90, plot_test=False):
    """
    get availability arrays of dataset, in percent
    output: (x,y)

    - data
    - thresh (-90 default): btw. -120 and 0
    - plot_test: dbg, don't output percent but all bins n xaxis

    >>> availability(range(-115,-10))
    ([0, 1], array([0.23809524, 0.76190476]))
    
    >>> availability(range(-200,500), plot_test=True)
    Traceback (most recent call last):
    Exception: programmer, you are ugly! (availability range doesn't make sense)
    
    >>> availability(range(-115,-10), plot_test=True)
    ([-310.0, -105.0, -45.0, 250.0], array([ 0, 25, 80,  0]))
    """

    dl = count_non_nan(data)

    bins = [-500,-120, thresh,0,500]
    binned, edges = np.histogram(a=data, bins=bins)

    if any(edges != bins):
        raise Exception("python is ugly")

    if (binned[0]) or (binned[len(binned)-1]):
        raise Exception("programmer, you are ugly! (availability range doesn't make sense)")

    if plot_test:
        x_plot_pos = bin_to_xaxis(bins)
        return x_plot_pos, binned
    else:
        return [0,1], binned[1:-1]/dl # omit first and last border-bins, only used for exception, also turn to percent
'''


def availability_frac(data, nan_bad=True):
    """ get availability fraction >= threshold
        - data (1D array)
        - threshold (included on good_count interval) - HARDCODED
        - nan_bad: NANs are bad?
            - True: missing datapoints (DEFAULT)
            - False: empty matrix elements (less to count, e.g. padding in some position_matrix)

        return good_count/total_count

    """
    # hardcoded thres - hardcoded as accessed across multiple repos in weird git nestings
    threshold=-90
    
    # condition input to 1D array
    data = np.array(data)
    data = roadkill(data)

    # counts
    total_count = len(data) # nan, good, bad
    nan_count = count_nan(data)
    good_count = len(data[data>=threshold])
    bad_count = len(data[data<threshold])
    
    # interprete NANs
    if nan_bad:
        bad_count += nan_count
    else:
        total_count -= nan_count

    if good_count+bad_count != total_count:
        raise Exception(f"{good_count=}+{bad_count=} != {total_count=}, {nan_bad=}")

    # return fraction
    return good_count/total_count



#-#-# module test #-#-#
if __name__ == '__main__': # test if called as executable, not as library
    integritycheck()#does not work f class functions?




    # # scalar element present: [5] # # #ToDo put into nanmean doctest as docu maybe
    #nanmean( np.array([[1,2,3],[3,np.nan],[5]], dtype="object") )
    
    #nanmean( pd.Series([[1,2,3],[3,np.nan],[5]]) )
    #AttributeError: 'list' object has no attribute 'dtype'
    #ValueError: setting an array element with a sequence. The requested array has an inhomogeneous shape after 1 dimensions. The detected shape was (6,) + inhomogeneous part.

    #nanmean( np.array([[1,2,3],[3,np.nan],[np.array([[1,2,3],[3,np.nan],[5]])]], dtype="object"), dtype="object" )
    #ValueError: setting an array element with a sequence. The requested array has an inhomogeneous shape after 1 dimensions. The detected shape was (3,) + inhomogeneous part.
    #nanmean( pd.Series([[1,2,3],[3,np.nan],[pd.Series([[1,2,3],[3,np.nan],[5]])]]) )
    #AttributeError: 'list' object has no attribute 'dtype'
    #ValueError: setting an array element with a sequence. The requested array has an inhomogeneous shape after 1 dimensions. The detected shape was (6,) + inhomogeneous part.
    #ValueError: zero-dimensional arrays cannot be concatenatednanmean( [roadkill(ele, hard=True) for ele in pd.Series([[1,2,3],[3,np.nan],[pd.Series([[1,2,3],[3,np.nan],[5]])]])] )
    #ValueError: zero-dimensional arrays cannot be concatenated

    # # no scalar element # #
    #nanmean( np.array([[1,2,3],[3,np.nan],[5,6]], dtype="object") )
    
    #nanmean( pd.Series([[1,2,3],[3,np.nan],[5,6]]) )
    
    #nanmean( pd.Series([[1,2,3],[3,np.nan],[pd.Series([[1,2,3],[3,np.nan],[5,6]])]]) )
    #AttributeError: 'list' object has no attribute 'dtype'
    #ValueError: setting an array element with a sequence. The requested array has an inhomogeneous shape after 1 dimensions. The detected shape was (6,) + inhomogeneous part.
    
    #nanmean( [roadkill(ele, hard=True) for ele in pd.Series([[1,2,3],[3,np.nan],[pd.Series([[1,2,3],[3,np.nan],[5,6]], dtype="object")]], dtype="object")] )
    #ValueError: zero-dimensional arrays cannot be concatenated

    #nanmean( [roadkill(ele) for ele in pd.Series([[1,2,3],[4,5,np.nan],[pd.Series([[1,2,3],[4,5,np.nan],[5,6]], dtype="object")]], dtype="object")] )

    #nanmean( np.array([roadkill(ele) for ele in np.array([[1,2,3],[4,5,np.nan],[np.array([[1,2,3],[4,5,np.nan],[5,6]], dtype="object")]], dtype="object")], dtype="object") )
    
