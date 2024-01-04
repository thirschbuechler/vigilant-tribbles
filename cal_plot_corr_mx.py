#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal plot_corr_mx

replacing calibrate_corr_mx_label in myink:
auto-calibrate to px size and drop a csv file

Created 02.01.24
@author: thirschbuechler
"""
import os
import numpy as np
import pandas as pd



try:
    import myink as mi
    import mailuefterl as ml
    import mystring as ms
    import ch_mx_lineartime as chx
    import detect_rectangle_pixel as drp

except:
    try:
        from vigilant_tribbles import myink as mi
        from vigilant_tribbles import mailuefterl as ml
        from vigilant_tribbles import mystring as ms
        from vigilant_tribbles import ch_mx_lineartime as chx
        from vigilant_tribbles import detect_rectangle_pixel as drp

    except:
        print("failed to import module directly or via submodule -  mind adding them with underscores not operators (minuses aka dashes, etc.)")


# define calfile and make sure its loaded from scriptfolder
cf = "plot_corr_mx_lookuptable.csv"
scriptfile = __file__
tail, head = os.path.split(scriptfile)
cf = os.path.abspath(os.path.join(tail, cf))


def plot_and_tell_deviation(pe, want_width_px, datalen, labellen, pixelscale):
    # gen labels
    label_ints = np.arange(0,datalen, dtype=np.int8)

    # elongate labels
    label_ints = ["".join([str(labeli) for _ in range(0,labellen)]) for labeli in label_ints]

    # gererate testdata
    #   - don't start at 0
    #   - make sure to have at least 2-3 values, otherwise detector cannot work (needs an extrema colored pixel - red)
    #   - also don't go above 7 diff element , then the gradient in plotted pixels doesn't get picked up in detect_rectangle_pixel
    #   --> make it simple: all ones, one maxima
    vec = np.ones(datalen)
    vec[0] = 11

    #make data mx
    mx = np.diag(vec)
    
    # ignore non-diagonal zeros
    mx[mx==0] = np.nan
    
    # plot and detection
    try:
        #optlabel = f"{datalens=}"# always clips on small, does it encourage to clip cb_label?
        optlabel = "" # nope, cb_label clips indepentent of this

        # plot
        kwargs = {"aspect":"square_cal"} # cal mode disables loading coeffs for pixelscale input
        clims=[]
        pe.plot_corr_mx(mx=mx,xlabels=label_ints, ylabels=label_ints, clims=clims, optlabel=optlabel, cb_label="1E", pixelscale=pixelscale, **kwargs)

        # save
        fig_name = "fig.png"
        pe.savefig(fname=fig_name, format="png", pad_inches=0)
        
        # detect
        minsize = 20 # gives smallest allowed area dimension (px), also used for scaling result
        r = drp.detect_colored_area(fig_name, "fig2.png", minsize = minsize, hsvmin = (0, 25, 25), hsvmax = (1, 255,255))
        
        # rm ele
        r = r[:-1] # ignore last element
        print(f"### {r=}")

        # assure it's vaguely square
        aspect = max(r)/min(r)
        aspectmax = 1.2
        print(aspect)
        if aspect < aspectmax:
            pass
        elif aspect > 100:
            # assume on very long thing smaller dimension is what we want
            r = min(r)
        else:
            raise Exception(f"pixeldetect got rect not square - {aspect=} < {aspectmax=}, {r=}")

        # turn into deviation
        deviation = abs(want_width_px-np.average(r))/want_width_px

        # cleanup - still get TRAIL:root:closing ' (empty figure title)' on both :( HACK doesnt work
        #pe.close(pe.get_fig()) # 
        pe.close() # any stray one

    except Exception as e:
        print(e)
        deviation = 1 # make it large to cancel iteration

    return deviation


def calibrate(want_width_px, labellens, datalens, px_arr):
    """ define a want_width_px and arrays of labellens, datalens for which to find pixelscales and write to csv
        px_arr:
            - at least two edges required for bintreesearch (pixelscales points)
            - can be array which is parsed from left to right for a valid starting point in case of an Exception"""

    # plot element
    pe = mi.myinkc()

    # output data frame
    df = pd.DataFrame()


    # loop
    for datalen in datalens:
        for labellen in labellens:

            # local fct with current params        
            def evalfct(param):
                return plot_and_tell_deviation(pe=pe, want_width_px=want_width_px, labellen=labellen, datalen=datalen, pixelscale=param)

            # 0.03: # 1px at 30px width
            maxdeviate=0.03
            #for pixelscale in np.arange(0.5,1.5,0.05):

            #    a = evalfct(pixelscale)
            #    print(datalen, labellen, pixelscale, a)
            
            pixelscale = None
            
            px_arr = list(px_arr)
            
            #right = px_arr.pop # giving it a fct pointer just dies xD HACK?
            right = px_arr.pop() 
            for left in px_arr:
                try:
                    pixelscale = ml.bintreesearch(evalfct=evalfct, maxdeviate=maxdeviate, left=left, right=right, echo=True)
                    if pixelscale:
                        print("yay")
                        break
                except Exception as e:
                    #print(f"{left} broke")
                    pass

            if pixelscale:
                new_row = pd.DataFrame([{"datalen":datalen, "pixelscale":pixelscale, "labellen":labellen, "want_width_px":want_width_px}])
                print(new_row)
                df = pd.concat([df, new_row], ignore_index=True)

    write_cal(df)


def get_cal():
    # get
    if os.path.exists(cf):
        df = pd.read_csv(cf)
        
        # reset index as write_cal uses concat and might have messed it up
        df.reset_index(drop=True, inplace=True)

    else:
        df = None

    # done
    return df

def write_cal(df):
    
    old = get_cal()
    
    df = pd.concat([old,df])

    df.to_csv(cf, index=False)


if __name__ == '__main__': # test if called as executable, not as library
    """
        labellen = 2: case labels are ascending ints
        labellen = 22: rest - HACK
        """

    calibrate(want_width_px=30, labellens = [2,22],datalens = np.arange(3,16), px_arr = np.arange(0,5,0.05))        
    
    # saz all40
        # impossible
        #calibrate(want_width_px=30, labellens = [2,20], datalens = [40], px_arr = [0,1])    
    # possible
    #calibrate(want_width_px=12, labellens = [2,22], datalens = [40], px_arr = np.arange(0,1,0.1))    
    #calibrate(want_width_px=12, labellens = [2,20], datalens = [20], px_arr = np.arange(0,1,0.1))    

    # vna usecase
    #calibrate(want_width_px=12, labellens = [21], datalens = [15], px_arr = np.arange(0,1,0.1))    

    #df = pd.DataFrame({'Unnamed: 0': {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10}, 'datalen': {0: 3, 1: 3, 2: 4, 3: 4, 4: 5, 5: 5, 6: 6, 7: 6, 8: 7, 9: 7, 10: 40}, 'pixelscale': {0: 0.6875, 1: 1.0625, 2: 0.671875, 3: 0.96875, 4: 0.6875, 5: 0.953125, 6: 0.75, 7: 0.984375, 8: 0.7875, 9: 1.0546875, 10: -0.19140625}, 'labellen': {0: 2, 1: 20, 2: 2, 3: 20, 4: 2, 5: 20, 6: 2, 7: 20, 8: 2, 9: 20, 10: 2}, 'deviation': {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1}})
    #df.to_csv(cf)

    #df = pd.read_csv(cf)
    #df = df.reset_index(drop=True)

    #print((df).to_dict())
    pass


