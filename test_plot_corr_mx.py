#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test plot_corr_mx

supplementing calibrate_corr_mx_label in myink

- manshow_graph: go through some combinations
- in main: plot it

Created 08.12.23
@author: thirschbuechler
"""

import numpy as np
import pandas as pd


try:
    import myink as mi
    import mystring as ms
    import ch_mx_lineartime as chx
except:
    try:
        from vigilant_tribbles import myink as mi
        from vigilant_tribbles import mystring as ms
        from vigilant_tribbles import ch_mx_lineartime as chx

    except:
        print("failed to import module directly or via submodule -  mind adding them with underscores not operators (minuses aka dashes, etc.)")


def human_graphrater(datalens=[], pixelscales=[], labellen=[], **kwargs):
    pe = mi.myinkc()

    # prep button insert
    rating = [] # "global" list from 1 to 5 stars
    df = pd.DataFrame()
    from matplotlib.widgets import Button

    class Index:

        def ok(self, event):
            rating.append(5)
            pe.close()

        def bad(self, event):
            rating.append(3)
            pe.close()

    # generate instance
    callback = Index()


    clims=[]

    paramlist = []
    # loop
    for datalen in datalens:
        for pixelscale in pixelscales:
    
            #paramlist.append({"datalen":datalen, "pixelscale":pixelscale})

            # gen labels
            folderlabels = np.arange(0,datalen, dtype=np.int8)

            # elongate labels?
            folderlabels = ["".join([str(flabel) for _ in range(0,labellen)]) for flabel in folderlabels]

            vec = np.random.random(size=datalen)
            mx = np.diag(vec)
            mx[mx==0] = np.nan
            
            kwargs = {"aspect":"square"} # HACK - doesnt work without
            try:
                optlabel = f"{datalens=}"# always clips on small, does it encourage to clip cb_label?
                optlabel = "" # nope, cb_label still clips
                pe.plot_corr_mx(mx=mx,xlabels=folderlabels, ylabels=folderlabels, clims=clims, optlabel=optlabel, cb_label="1E", pixelscale=pixelscale, **kwargs)

                # add controls
                # https://matplotlib.org/stable/gallery/widgets/buttons.html
                fig = pe.get_fig()
                axbad = fig.add_axes([0.7, 0.05, 0.1, 0.075])
                axok = fig.add_axes([0.81, 0.05, 0.1, 0.075])
                bok = Button(axok, 'OK')
                bok.on_clicked(callback.ok)
                bbad = Button(axbad, 'Bad')
                bbad.on_clicked(callback.bad)
                
                pe.show()
            except Exception as e:
                rating.append(1)
            
            
            new_row = pd.DataFrame([{"datalen":datalen, "pixelscale":pixelscale, "labellen":labellen, "rating":rating[0]}])
            print(new_row)
            df = pd.concat([df, new_row], ignore_index=True)
            rating = [] # reset "global" list

    return (df)


def wf_from_df(df):

    pixelscales = np.array(df['pixelscales'].unique())
    datalens = np.array(df['datalen'].unique())

    print(df.head(0))

    vint = np.vectorize(int)
    pixelscales = vint(pixelscales*10)  #*10 workaround to get int and fit with mx making
        # def make_mx_new(df, d_col="RSSI", t_col = "timestamp", x_col = "CH", xmax = 40, dtype='float16', lintime=True):
    mx = chx.make_mx_new(df, d_col="outcome", t_col="datalen", x_col="pixelscale", xmax=max(pixelscales)+1) # hack lens+1 if issue
    datalens = np.array(datalens)

    # plot
    pe = mi.myinkc()
    pe.subplots()
    pe.waterfall(mx, x_axis=pixelscales, yticks=datalens, cb_label="badness (blue ok, green bad, red autobad)")
    pe.xlabel("pixelscale*10") #*10 workaround to get int and fit with mx making
    pe.ylabel("datalen")

    pe.show()


def get_lsq_from_df(df):

    # select best ratings only
    df = df[df["rating"]==5]

    y = df["pixelscale"]
    x = df["datalen"]
    
    # get lsq
    pe = mi.myinkc()
    k,d = pe.LSQ_line(x,y)

    print(k,d) #-0.18444444444444447 2.357777777777778

    # calc line
    pixelscales = datalens*k + d

    # plot
    pe.subplots()
    pe.plot(datalens, pixelscales, label="optimal")
    pe.scatter(x, y, label="samples", color="orange")
    pe.ylabel("pixelscale")
    pe.xlabel("datalen")
    pe.title(f"pixelscale via datalen and fixed {labellen=}")

    pe.show()



if __name__ == '__main__': # test if called as executable, not as library
    
    # testparams
    datalens = np.arange(3,8)
    
    #k, d = -0.18444444444444447, 2.357777777777778
    #pixelscales = datalens*k + d
    #k,d = 0.06916666666666654, 1.3663888888888895
    #pixelscales = pixelscales*k + d
    #pixelscales = datalens*k + d

    #pixelscales = np.ones(len(datalens)) * 1.7
    #pixelscales = [1]
    
    
    pixelscales = np.arange(0.9,1.1,0.05)

    labellen = 20 # good for most, for datalen=40 however labellen=2 needed

    df = human_graphrater(datalens=datalens, pixelscales=pixelscales, labellen=labellen)

    # graph test dummydata
    #results = [1,3,5]
    #pixelscales=[2,5,1]
    #datalens=[1,2,3]

    #datalens = np.array([3,4,5,6,7])
    #pixelscales =  np.array(list(range(1,20,1)))/10
    #plot_txt(dataset1, pixelscales=pixelscales, datalens=datalens)

    get_lsq_from_df(df)

