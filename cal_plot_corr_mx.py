#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cal plot_corr_mx

replacing calibrate_corr_mx_label in myink:
auto-calibrate to px size and drop a csv file

Created 02.01.24
@author: thirschbuechler
"""
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



def plot_and_tell_deviation(pe, want_width_px, datalen, labellen, pixelscale):
    # gen labels
    label_ints = np.arange(0,datalen, dtype=np.int8)

    # elongate labels?
    label_ints = ["".join([str(labeli) for _ in range(0,labellen)]) for labeli in label_ints]

    vec = np.array(np.arange(1,datalen-1), dtype=np.float16)

    mx = np.diag(vec)
    mx[mx==0] = np.nan
    
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
        #print(f"### {r=}")

        # assure it's vaguely square
        aspect = max(r)/min(r)
        aspectmax = 1.2
        if aspect < aspectmax:
            pass
        else:
            raise Exception(f"pixeldetect got rect not square - {aspect=} < {aspectmax=}, {r=}")

        # turn into deviation
        deviation = abs(want_width_px-np.average(r))/want_width_px

        # cleanup - still get TRAIL:root:closing ' (empty figure title)' on both :( HACK doesnt work
        #pe.close(pe.get_fig()) # 
        pe.close() # any stray one

    except Exception as e:
        #print(e)
        deviation = 1 # make it large to cancel iteration

    return deviation


def calibrate(want_width_px=30, labellens = [2,20],datalens = np.arange(3,8)):

    # plot element
    pe = mi.myinkc()

    # output data frame
    df = pd.DataFrame()


    # loop
    for datalen in datalens:
        for labellen in labellens:
            
            deviation = 1
            #pixelscales = np.arange(0.5,1.5,0.05)
        
            def evalfct(param):
                return plot_and_tell_deviation(pe=pe, want_width_px=want_width_px, labellen=labellen, datalen=datalen, pixelscale=param)

            # 0.03: # 1px at 30px width
            maxdeviate=0.03
            #for pixelscale in np.arange(0.5,1.5,0.05):

            #    a = evalfct(pixelscale)
            #    print(datalen, labellen, pixelscale, a)
            
            pixelscale = None
            for left in np.arange(0.5,1.5,0.05):
                try:
                    pixelscale = ml.bintreesearch(evalfct=evalfct, maxdeviate=maxdeviate, left=left, right=1.5, echo=True)
                    if pixelscale:
                        print("yay")
                        break
                except Exception as e:
                    #print(f"{left} broke")
                    pass

            if pixelscale:
                new_row = pd.DataFrame([{"datalen":datalen, "pixelscale":pixelscale, "labellen":labellen, "deviation":deviation}])
                print(new_row)
                df = pd.concat([df, new_row], ignore_index=True)

    df.to_csv("plot_corr_mx_lookuptable.csv")




if __name__ == '__main__': # test if called as executable, not as library
    
    calibrate()
    


