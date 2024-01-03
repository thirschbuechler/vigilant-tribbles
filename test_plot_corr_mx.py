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


def graph_examiner(datalens=[], pixelscales=[], labellen=[], human=True, **kwargs):
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

            if human: # prettier to look at
                vec = np.random.random(size=datalen)
            else: # easier to eval - only have ascending data, ergo one red square                
                vec = np.array(np.arange(1,datalen-1), dtype=np.float16)

            mx = np.diag(vec)
            mx[mx==0] = np.nan
            
            kwargs = {"aspect":"square"} # HACK - doesnt work without
            try:
                optlabel = f"{datalens=}"# always clips on small, does it encourage to clip cb_label?
                optlabel = "" # nope, cb_label still clips
                pe.plot_corr_mx(mx=mx,xlabels=folderlabels, ylabels=folderlabels, clims=clims, optlabel=optlabel, cb_label="1E", pixelscale=pixelscale, **kwargs)

                if human:
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
                else:
                    fig_name = "fig.png"
                    pe.savefig(fname=fig_name, format="png", pad_inches=0)
                    
                    minsize = 20 # gives smallest allowed area dimension (px), also used for scaling result
                    r = drp.detect_colored_area(fig_name, "fig2.png", minsize = minsize, hsvmin = (0, 25, 25), hsvmax = (1, 255,255))
                    r = r[:-1] # ignore last element
                    print(f"### {r=}")

                    # is it vagely a square?
                    aspect = max(r)/min(r)
                    aspectmax = 1.2
                    if aspect < aspectmax:
                        pass
                    else:
                        raise Exception(f"pixeldetect failed - {aspect=} < {aspectmax=}, detected {r}")

                    # average of both dimensions, over minsize
                    frac = (np.sum(r))/(2*minsize)
                    
                    # turn into deviation
                    deviation = abs(frac-1)
                    
                    # put onto 5er scale - legacy manual rating reason i guess
                    res = 5-deviation*5
                    
                    if res > 5:
                        pe.subplots()
                        pe.pic(fig_name)
                        pe.title("failed - larger than max rating - pixel detection result too big, multiples?")
                        pe.show()
                    rating.append(res)
                
                    pe.close() # any stray one

                    
            except Exception as e:
                print(e)
                rating.append(0.001)
            
            
            new_row = pd.DataFrame([{"datalen":datalen, "pixelscale":pixelscale, "labellen":labellen, "rating":rating[0]}])
            print(new_row)
            df = pd.concat([df, new_row], ignore_index=True)
            rating = [] # reset "global" list

    return (df)


def wf_from_df(df=pd.DataFrame()):
    #df.to_csv("aaa.csv") # doesn't work or goes to where??
        
    # workaround for chx.mace_mx_new only works w ints
    #factor = 1000
    #df["pixelscale"] = df["pixelscale"].apply(lambda a: a*factor)
    #df["rating"] = df["rating"].apply(lambda a: a*factor)

    # get 
    factor = 1
    pixelscales = np.array(df['pixelscale'])
    datalens = np.array(df['datalen'])
    data = np.array(df["rating"])
    #print(f"{data=}")
    
    boolvec = (data == np.average(data) * np.ones(np.size(data)))
    if np.all(boolvec):
        identical = True
    else:
        identical = False

    x_axis = np.array(df['pixelscale'].unique())
    y_axis = np.array(df['datalen'].unique())

    #print(pixelscales)

    # create repeating lookup indices lists:
    # array.index() equiv for numpy,
    # as basearrays are unique() it is a 1d list
    x_vect = [np.where(x_axis == item)[0] for item in pixelscales]
    y_vect = [np.where(y_axis == item)[0] for item in datalens]

    # de-nest them
    x_vect = np.array(ml.roadkill(x_vect), dtype=int)
    y_vect = np.array(ml.roadkill(y_vect), dtype=int)
    #print(x_vect)

    # make matrix
    mx=np.empty(shape=(np.size(x_axis), np.size(y_axis)))
    mx[:] = np.nan

    # assign
    mx[x_vect,y_vect]=data

    
    #print(f"{np.shape(mx)=}")

    # plot
    pe = mi.myinkc()
    pe.subplots()
    pe.waterfall(mx, x_axis=x_axis, yticks=y_axis, cb_label="badness (blue ok, green bad, red autobad)")
    pe.imshow(mx)
    pe.xlabel(f"pixelscale*{factor}") 
    pe.ylabel("datalen")
    if identical:
        pe.title("identical values - not a plot error")

    pe.show()

"""
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
"""

def calibrate(labellen = 20,datalens = np.arange(3,8), pixelscales = np.arange(0.5,1.5,0.05)):
    #labellen = 20 # good for most, for datalen=40 however labellen=2 needed

    df = graph_examiner(datalens=datalens, pixelscales=pixelscales, labellen=labellen, human=False)

    # graph test dummydata
    #results = [1,3,5]
    #pixelscales=[2,5,1]
    #datalens=[1,2,3]

    #datalens = np.array([3,4,5,6,7])
    #pixelscales =  np.array(list(range(1,20,1)))/10
    #plot_txt(dataset1, pixelscales=pixelscales, datalens=datalens)

    #wf_from_df(df)

    #get_lsq_from_df(df)

    df.to_csv("plot_corr_mx_lookuptable.csv")


def test_cal():
    df = pd.read_csv("plot_corr_mx_lookuptable.csv")
    #wf_from_df(df)
    df = df[df["rating"] > 4]
    #wf_from_df(df)



if __name__ == '__main__': # test if called as executable, not as library
    
    calibrate()
    #test_cal()


