# some general computation bla

import numpy as np
import warnings # numpy nanzero zeroslice stuff


def sample_var(*args, **kwargs):
    """ sample variance
        "provides an unbiased estimator of the variance of a hypothetical infinite population"

        be careful with multidim, "axis" kwarg might help

    # [1,5], mean=6, n=2, (2²+2²)/(n-1)=8
    >>> sample_var([1,5])
    8.0

    """
    kwargs["ddof"]=1
    return np.var(*args, **kwargs)


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


def histo_weighter(percent=False, basearray = 0, **kwargs):
    if percent:
            raise Exception("use mailuefterl histogram and plot") # too lazy to fix again
    return kwargs


def histogram(x=[], percent=False, autorange=False, basearray = None, **kwargs):
    """ weighted histograms
        - x (arr): data
        - autorange (bool): range=[nanmin(x), nanmax(x)]
        - percent (bool): weigh to reflect percent
        - basearray (arr): use countnonnan(basearray) as percent base

        BE CAUTIOUS OF np.nan in weights! no-output, even for many non-zero weights can happen
    """

    if autorange:
        kwargs["range"] = (nanmin(x), nanmax(x))

    # which percentbase
    if type(basearray) != type(None):
        if not len(basearray): # if len 0
            basearray = x
        else:
            #basearray = basearray # ok
            pass
    else: # if no basearray
        basearray = x

    if percent:
        weights=np.ones(np.shape(x)) / count_non_nan(basearray)
        kwargs["weights"]=weights
    # numpy hist
    n, bins = np.histogram(a=x,**kwargs)

    return n,bins
    """
    attention: 
    default parameter in np.histogram is "a"
        numpy histogram ignores weights, so re-do n afterwards
    default parameter in matplotlib.hist is "x"
        mpl hist works with weights as expected
    """


def integritycheck():
    """ better call doctest """
    import doctest
    print("performing doctest test..")
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
    
def mx_diag_mirror(X):
    # https://stackoverflow.com/questions/16444930/copy-upper-triangle-to-lower-triangle-in-a-python-matrix/42209263
    X = np.triu(X) #remove NANs of lower triag, which were used to hide redundancy
    return X + X.T - np.diag(np.diag(X))
    

def singledim_mod_testdata():
    data = np.array([[1,2],[3,4]])
    data = [data,data]
    data = [data,data]
    return data

def singledim_mod(data):
    """ takes multidimensional array and flattens all but first one - useful for boxplot(), etc.
        aka dimred, dimension reduction, ...
        --> only keep first dimension
        
        - I/O: np.array()

    >>> np.shape(singledim_mod(singledim_mod_testdata()))
    (2, 8)
    """
    #print(f"{np.shape(data)=}")
    args = []
    args = np.shape(data)
    data = np.reshape(data, newshape=(args[0], np.prod(args[1:])))
    return data


def roadkill(thing, hard=False):
    """ flatten if possible - remove any dimensions and make a list """
    if (hasattr(thing, "__iter__")):
        if not hard:
            return(thing.flatten()) # please be flat
        else:
            # sudo be_flat
            # - join np.arrays in list via conc
            # - then join lists via ravel)
            return(np.concatenate(thing).ravel())

    else:
        return thing
        
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
    
