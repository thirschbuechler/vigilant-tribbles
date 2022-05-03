"""
reshaper.py

unit-tested data marginalization

by thirschbuechler, 08.03.22
"""
import numpy as np
try:
    from myink import myinkc
except:
    try:
        from vigilant_tribbles.myink import myinkc
    except:
        print("failed to import module directly or via submodule -  mind adding them with underscores not operators (minuses aka dashes, etc.)")


def is_odd(num):
    return num & 0x1

def testdata_50():
    return np.reshape(np.arange(1, 51), newshape=(5,10))

def testdata_60_overlarge(count=1):
    """ add one or more columns to test-delete """ 
    mx = testdata_50()
    extra = np.arange(1,6)
    #np.row_stack([mx.T, extra])
    for i in range(count):
        mx = np.column_stack([mx, extra])
    return mx

# TODO test with a 1000x151 made up file in hist to "finally" prove it's not shit
def row_window_eval(mx, eval, win_len=-1, cols_out=-1, outp_zeros_allowed=False, dtype=np.float64):
    """ average input mx along first (0) axis
        - mx: input mx
        - eval: fct to marginalize multiple items into one
        - either, or both:
        - - win_len: window length to apply eval over along row
        - - cols_out: how many columns after windowing
        - outp_zeros_allowed: absorb runtime warnings, such as np.nanmean(0)==0
        
        # tests overview
        - 1) along right axis?
        - 2) with manual parameter
        - 3) one col too much
        - 4) two cols too much
        >>> row_window_eval(mx=testdata_50(), eval=np.mean, win_len=2)[0]
        array([[ 1.5,  3.5,  5.5,  7.5,  9.5],
               [11.5, 13.5, 15.5, 17.5, 19.5],
               [21.5, 23.5, 25.5, 27.5, 29.5],
               [31.5, 33.5, 35.5, 37.5, 39.5],
               [41.5, 43.5, 45.5, 47.5, 49.5]])
        >>> row_window_eval(mx=testdata_50(), eval=np.mean, win_len=2, cols_out=5)[0]
        array([[ 1.5,  3.5,  5.5,  7.5,  9.5],
               [11.5, 13.5, 15.5, 17.5, 19.5],
               [21.5, 23.5, 25.5, 27.5, 29.5],
               [31.5, 33.5, 35.5, 37.5, 39.5],
               [41.5, 43.5, 45.5, 47.5, 49.5]])
        >>> row_window_eval(mx=testdata_60_overlarge(), eval=np.mean, win_len=2, cols_out=5)[0]
        array([[ 1.5,  3.5,  5.5,  7.5,  9.5],
               [11.5, 13.5, 15.5, 17.5, 19.5],
               [21.5, 23.5, 25.5, 27.5, 29.5],
               [31.5, 33.5, 35.5, 37.5, 39.5],
               [41.5, 43.5, 45.5, 47.5, 49.5]])
        >>> row_window_eval(mx=testdata_60_overlarge(count=2), eval=np.mean, win_len=2, cols_out=5)[0]
        array([[ 1.5,  3.5,  5.5,  7.5,  9.5],
               [11.5, 13.5, 15.5, 17.5, 19.5],
               [21.5, 23.5, 25.5, 27.5, 29.5],
               [31.5, 33.5, 35.5, 37.5, 39.5],
               [41.5, 43.5, 45.5, 47.5, 49.5]])
    """

    # trim if both given and axis too long, till it fits
    if (win_len+1) and (cols_out+1):
        # row is and want lengths
        is_w, is_len = np.shape(mx)
        want_len = cols_out * win_len

        if (want_len) < is_len:
            #print(mx)
            delete_indices = [(is_len - i -1) for i in np.arange(is_len-want_len)]# delete last ones, count from 0
            #print(delete_indices)
            mx = np.delete(arr=mx,obj=delete_indices,axis=1)
            #print(mx)
        
        elif want_len > is_len:
            #add_indices = [(want_len - i -1) for i in np.arange(want_len-is_len)]
            pad=np.empty(shape=(is_w, want_len-is_len))
            pad[:] = np.nan
            mx = np.append(mx,pad,axis=1)
    
    # marginalize frequencies to channels ("reshape n eval")
    mx2 = np.array([np.reshape(row, newshape=(win_len,cols_out), order="F") for row in mx], dtype=dtype) # mx2: (pos, freqbins, subele)
    if outp_zeros_allowed:
        import warnings
        # I expect to see RuntimeWarnings in this block - a mean(0) warning
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            out_mx = eval(mx2,axis=1) # evaluate temp axis - is inbetween first (0) and last (2)
    else:
        out_mx = eval(mx2,axis=1) # evaluate temp axis - is inbetween first (0) and last (2)

    # shapestring
    shapestr=("shapes of input mx: {}, intermed mx: {} and out_mx: {}".format( *[np.shape(x) for x in [mx, mx2, out_mx] ] ))

    return out_mx, shapestr


def col_window_eval(mx, *args, rows_out = -1, **kwargs):
    """ doc: see row_window_eval
        - cols_out here: rows_out"""
    out_mx, shapestr = row_window_eval(mx.T, *args, cols_out = rows_out, **kwargs)
    
    banner = " ! (y,x) shapestr! "
    shapestr = banner+shapestr+banner
    return out_mx.T, shapestr


def integritycheck():
    """ better call doctest """
    import doctest
    print("performing doctest test..")
    res=doctest.testmod() # process doctest methods
    print(res)
    print("attempted==succeeded, if no fails\n")


def plot_testdata():
    # # dummy data # #
    mx=testdata_50()

    # # eval # #
    pos_ch_mx, shapestr = row_window_eval(mx=mx, eval=np.mean, win_len=2)

    # # plot n print # #
    pe = myinkc()
    pe.subplots(nrows=2, ncols=2)
    #print(mx)
    #print(np.shape(mx))#5, 10
    pe.imshow(mx)
    pe.title(np.shape(mx))
    pe.ax_onward()

    #print(np.shape(mx2))#5,2,10
    #print(mx2)
    #pe.imshow(mx2)
    #pe.title(np.shape(mx2))
    pe.ax_onward()

    #print(np.shape(pos_ch_mx))
    print(pos_ch_mx)


    pe.imshow(pos_ch_mx)
    pe.title(np.shape(pos_ch_mx))
    pe.common_cb_lims(mx) # sets common colorange, empties imim array  # only needs original mx data since output mean is "subspace"

    pe.show()


if __name__ == '__main__': # test if called as executable, not as library, regular prints allowed
    plot_testdata() # further stuff: rssi-waterfall-dummy
    integritycheck()