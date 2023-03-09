import pandas as pd
import numpy as np

import numpy as np
try:
    from myink import myinkc
    import reshaper as rs
    import mailuefterl as ml
except:
    try:
        from vigilant_tribbles.myink import myinkc
        import vigilant_tribbles.reshaper as rs
        import vigilant_tribbles.mailuefterl as ml
    except:
        print("failed to import module directly or via submodule -  mind adding them with underscores not operators (minuses aka dashes, etc.)")


from scipy.sparse import lil_matrix, bsr_array # needs scipy 1.8.0!!


def make_mx(df):

    RSSIs = df.RSSI
    CHs = df.CH
    timestamps = df.timestamp

    bt_ch_max=40

    # make matrices
    mx=np.empty(shape=(bt_ch_max, np.size(timestamps)))# doesn't work with td for some reason
    mx[:] = np.nan
    t = np.arange(0,np.size(timestamps))

    # assign
    mx[CHs,t]=RSSIs

    return mx.T


def make_mx_new(df, d_col="RSSI", t_col = "timestamp", x_col = "CH", xmax = 40, dtype='float16', lintime=True):
    """ 
    takes a dataframe, output matrix
    - column selectors (str):
    - -  d_col .. data (eg RSSI)
    - -  t_col .. timestamp
    - -  x_col .. x_axis
    - xmax: dimension x-axis
    - dtype (of mx), e.g.
    - - float16 - default (has np.nan, less than float64 ram)
    - - uint8 would be better but no np.nan
    - - float64 is default but prohibitively large
    """
    # ingress
    RSSIs = np.array(df[d_col], dtype=int)
    CHs = np.array(df[x_col], dtype=int)
    timestamps = np.array(df[t_col], dtype=int)

    if lintime:
        t0 = min(timestamps)
        t = np.arange(0, max(timestamps)-t0+1)

        # make matrices
        mx=np.empty(shape=(xmax, np.size(t)),dtype=dtype)
        mx[:] = np.nan

        # assign
        mx[abs(CHs),timestamps-t0]=RSSIs
    else:
        t0 = 0
        t = np.arange(0, np.size(timestamps))
        
        # make matrices
        mx=np.empty(shape=(xmax, np.size(timestamps)),dtype=dtype)
        mx[:] = np.nan

        # assign
        mx[abs(CHs),t]=RSSIs


    return mx.T


def make_lil_mx(df, d_col="RSSI", t_col = "timestamp", x_col = "CH", xmax = 40, dtype='float16', lintime=True):
    """ 
    takes a dataframe, output matrix
    - column selectors (str):
    - -  d_col .. data (eg RSSI)
    - -  t_col .. timestamp
    - -  x_col .. x_axis
    - xmax: dimension x-axis
    - dtype UNUSED
    """
    # ingress
    RSSIs = np.array(df[d_col], dtype=int)
    CHs = np.array(df[x_col], dtype=int)
    timestamps = np.array(df[t_col], dtype=int)

    if lintime:
        t0 = min(timestamps)
        t = np.arange(0, max(timestamps)-t0+1)

        # make matrices
        mx=lil_matrix((xmax, np.size(t)) )
        #mx[:] = np.nan

        # assign
        mx[CHs,timestamps-t0]=RSSIs
    else:
        t0 = 0
        t = np.arange(0, np.size(timestamps))
        
        # make matrices
        mx=lil_matrix((xmax, np.size(timestamps)))#,dtype=dtype) # dtype ruins it
        #mx[:] = np.nan # not necessary i think

        # assign
        mx[CHs,t]=RSSIs

    return(mx.T)



#-#-# module test #-#-#
if __name__ == '__main__': # test if called as executable, not as library
    
    # testdata
    timestamps = [151, 3000, 3500, 5555, 6000]
    RSSIs = [-40, -50, -90, -69, -60]
    CHs = [30, 3, 20, 6, 3]
    df = pd.DataFrame(np.array([timestamps, RSSIs, CHs]).T, columns = ["timestamp", "RSSI", "CH"])

    mx = make_mx(df)
    mx2 = make_mx_new(df)

    rows_out = 100
    for cut in [True, False]:
        n = np.shape(mx2)[0]
        if cut:
            n_snake = ml.auto_floor(n)
        else:
            n_snake = ml.auto_ceil(n)


        win_len = int(n_snake / rows_out)

        kwargs_common =dict(win_len = win_len, rows_out = rows_out, outp_zeros_allowed=True)
        mx3, shapestr = rs.col_window_eval(mx = mx2, eval = np.nanmean, **kwargs_common)
        
        d = n - n_snake
        mode = "test"
        if cut:
            sup = ("wf: {}-cutting {} equal-spaced datapoints away, {:.1f}%".format(mode, d, d/n * 100))
        else:
            d=-d
            sup = ("wf: {}-nan_padding {} equal-spaced datapoints onto end, {:.1f}%".format(mode, d, d/n * 100))

        # plot #
        pe = myinkc()
        pe.subplots(ncols=3)
        ikwargs_common =dict(aspect="auto")

        pe.imshow(mx, **ikwargs_common)
        pe.yticklabels(timestamps)
        pe.ylabel("timestamps")
        pe.xlabel("Silabs BLE CH")
        pe.title("orig mx")
        
        pe.ax_onward()
        pe.imshow(mx2, **ikwargs_common)
        pe.ylabel("abs time")
        pe.xlabel("Silabs BLE CH")
        pe.title("new mx")
        
        pe.ax_onward()
        pe.imshow(mx3, **ikwargs_common)
        pe.ylabel("binned time")
        pe.xlabel("Silabs BLE CH")
        pe.title("new mx, avg and {} data only".format(rows_out))

        pe.suptitle(sup)
        pe.autoscale_fig()# fix hspace vspace etc
    pe.show()