# some general computation bla

import numpy as np
import warnings # numpy nanzero zeroslice stuff


def dummy(*args,**kwargs):
    pass # NOP - do nothing


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


def bin_to_xaxis(bins):
    """
    takes a histo bin array and returns the corresponding x-axis
    >>> bin_to_xaxis([0,1,2])
    [0.5, 1.5]
    """
    xaxis = [bins[i]+(bins[i+1]-bins[i])/2 for i in range(0,len(bins)-1)]
    return xaxis


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

def is_ragged(a):
    return get_shape(a) is None

def integritycheck():
    """ better call doctest """
    import doctest
    print(f"doctest called in ({__file__})")
    res=doctest.testmod() # process doctest methods
    print(res)
    print("attempted==succeeded, if no fails\n")


# HACK all runtime warnings of one fct ignored
# ToDo only ignore zeromean nan slice ones
def babysit(eval, *args, **kwargs):
    """ numpy nan-operation silencer
    
        nan-matrices shall be allowed to have means over nans or zeros without giving a warning,
        expect to see RuntimeWarnings otherwise
    """

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        return eval(*args,**kwargs)
    
    # alternatively (even thouth with_context is superior):
    # np.seterr(divide='ignore', invalid='ignore') # temp disable for nan operations
    # nan operations
    # np.seterr(divide='warn', invalid='warn') # re-enable
        
        
def nanmean(*args, **kwargs):
    return babysit(np.nanmean,*args, **kwargs)

def nanmax(*args, **kwargs):
    return babysit(np.nanmax,*args, **kwargs)

def nanmin(*args, **kwargs):
    return babysit(np.nanmin,*args, **kwargs)

def divide(*args, **kwargs):
    return babysit(np.divide,*args, **kwargs)

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

    if i==1:
        return [np.array([ 17,  14,  10,  47, 171,  44, 105,  91,  88,  14])]

def singledim_mod(data):
    """ takes multidimensional array and flattens all but first one - useful for boxplot(), etc.
        aka dimred, dimension reduction, ...
        --> only keep first dimension
        
        - I/O: np.array()

    >>> np.shape(singledim_mod_testdata(0))
    (2, 2, 2, 2)
    >>> np.shape(singledim_mod(singledim_mod_testdata(0)))
    (2, 8)
    >>> np.shape(singledim_mod_testdata(1))
    (1, 10)
    >>> np.shape(singledim_mod(singledim_mod_testdata(1)))
    (1, 10)

    """
    #print(f"{np.shape(data)=}")
    args = []
    args = np.shape(data)
    data = np.reshape(data, newshape=(int(args[0]), int(np.prod(args[1:]))))
    #if np.shape(data)[0] == 1:
    #    data = data[0]
    #if np.shape(data)[0] == 1:
    #    raise Exception("singledim_mod failed - shape==1")
    #print(np.shape(data))
    return data


def roadkill(thing, hard=False):
        """ flatten if possible - remove any dimensions and make a list 
        
        >>> np.shape(singledim_mod_testdata(0))
        (2, 2, 2, 2)
        >>> np.shape(roadkill(singledim_mod_testdata(0)))
        (16,)
        >>> np.shape(singledim_mod_testdata(1))
        (1, 10)
        >>> np.shape(roadkill(singledim_mod_testdata(1)))
        (10,)
        
        """
        if not (type(thing) == type(np.array([1]))):
                thing = np.array(thing, dtype="object")
        if np.shape(thing) == np.shape(1): # numpy shape returns warning ragged nested sequences, unless dtype=obj 
            return thing # no dimension
        elif (hasattr(thing, "__iter__")):
            
            if not hard:
                return(thing.flatten()) # please be flat
            else:
                # sudo be_flat
                # - join np.arrays in list via conc
                # - then join lists via ravel)
                # add a dummy dimension
                return(np.concatenate(thing).ravel())

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
    
