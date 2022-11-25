# some general computation bla

import numpy as np
import warnings # numpy nanzero zeroslice stuff


def bin_to_xaxis(bins):
    """
    takes a histo bin array and returns the corresponding x-axis
    >>> bin_to_xaxis([0,1,2])
    [0.5, 1.5]
    """
    xaxis = [bins[i]+(bins[i+1]-bins[i])/2 for i in range(0,len(bins)-1)]
    return xaxis


def count_non_nan(data):
    return np.count_nonzero(~np.isnan(data))


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


def histo_weighter(kwargs, percent):
    """ 
    return weights in kwargs if data aka x present and percent True
    both used in myinkc.histo and in mailuefterl.histogram
    
    default parameter in np.histogram is "a"
    default parameter in matplotlib.hist is "x"
    """
    if percent:
            # - find data or insert into dict
            # - insert weights
            if "x" in kwargs:
                x = kwargs["x"]
            else:
                raise Exception("percent switch needs \"x=\" data kwarg")
                #x = args[0]
                #kwargs["x"] = x
            weights=np.ones(np.shape(x)) / count_non_nan(x) # NOT len() - ones need to have same shape, not np.size (returns also non-nan elements and skews percent)

            kwargs["weights"] = weights
    return kwargs


def histogram(percent=False, **kwargs):
    kwargs = histo_weighter(percent=percent, kwargs=kwargs)
    # remove x param from keyw-args
    x=kwargs["x"]
    kwargs.pop("x")
    # insert x-param as non-keyw, since
    #      default parameter in np.histogram is "a" 
    #       default parameter in matplotlib.hist is "x" 
    return np.histogram(x,**kwargs)


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
    # numpy nanzero zeroslice stuff
    # nan-matrices shall be allowed to have means over nans or zeros without giving a warning
    # I expect to see RuntimeWarnings in this block - a mean(0) warning
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        return eval(*args,**kwargs)
        
def nanmean(*args, **kwargs):
    return babysit(np.nanmean,*args, **kwargs)

def nanmax(*args, **kwargs):
    return babysit(np.nanmax,*args, **kwargs)

def nanmin(*args, **kwargs):
    return babysit(np.nanmin,*args, **kwargs)

def mx_diag_mirror(X):
    # https://stackoverflow.com/questions/16444930/copy-upper-triangle-to-lower-triangle-in-a-python-matrix/42209263
    X = np.triu(X) #remove NANs of lower triag, which were used to hide redundancy
    return X + X.T - np.diag(np.diag(X))
    
#-#-# module test #-#-#
if __name__ == '__main__': # test if called as executable, not as library
    integritycheck()#does not work f class functions?
    
