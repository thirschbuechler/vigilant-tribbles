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
    #import mystring as ms
    import ch_mx_lineartime as chx
except:
    try:
        from vigilant_tribbles import myink as mi
        #from vigilant_tribbles import mystring as ms
        from vigilant_tribbles import ch_mx_lineartime as chx

    except:
        print("failed to import module directly or via submodule -  mind adding them with underscores not operators (minuses aka dashes, etc.)")


def manshow_graph(**kwargs):
    pe = mi.myinkc()

    # prep button insert
    results = []
    from matplotlib.widgets import Button

    class Index:

        def ok(self, event):
            results.append("ok")
            #print(event)# button_release_event: xy=(536, 45) xydata=(0.2749999999999986, 0.5833333333333334) button=1 dblclick=False inaxes=Axes(0.81,0.05;0.1x0.075)
            pe.close()

        def bad(self, event):
            results.append("bad")
            pe.close()

    # generate instance
    callback = Index()

    # testparams
    datalens = range(3,8)
    plens = [0.1,0.5,0.8, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2]
    labellen = 20
    clims=[]

    paramlist = []
    # loop
    for datalen in datalens:
        for pixelscale in plens:
    
            paramlist.append({"datalen":datalen, "pixelscale":pixelscale})

            # gen labels
            folderlabels = np.arange(0,datalen, dtype=np.int8)

            # elongate labels?
            folderlabels = ["".join([str(flabel) for _ in range(0,labellen)]) for flabel in folderlabels]

            vec = np.random.random(size=datalen)
            mx = np.diag(vec)
            mx[mx==0] = np.nan
            
            kwargs = {"aspect":"square"} # HACK - doesnt work without
            try:
                pe.plot_corr_mx(mx=mx,xlabels=folderlabels, ylabels=folderlabels, clims=clims, optlabel=f"{datalens=}", cb_label="1E", pixelscale=pixelscale, **kwargs)

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
                #results.append(f"autobad: {e}")
                results.append(f"autobad")

    evaluations = zip(paramlist, results)

    return (list(evaluations))



def plot_txt(txt, pixelscales=[], datalens=[]):
    pe = mi.myinkc()
    #import matplotlib.pyplot as plt
    #fig, ax = plt.subplots()
    pe.subplots()

    
    data = []
    for dicto, outcome in txt:

        # convert outcome to int
        if outcome=="OK" or outcome=="ok":
            c=10
        elif outcome=="Bad" or outcome=="bad":
            c=5
        elif (outcome=="autobad") or ("autobad" in outcome):
            c=1
        else:
            raise Exception(f"not valid: {outcome=}")
        
        # don't try to hold-plot
        #pe.scatter(dicto["datalen"], dicto["pixelscale"], c=c)
        
        # save for later
        xi,yi,zi = (dicto["datalen"], int(dicto["pixelscale"]*10), c)
        data.append([xi,yi,zi])
    

    #x,y,z = data
    #df = pd.DataFrame(columns=["datalen", "pixelscale", "outcome"])
    #df.append(x,y,z)
    data = np.array(data)
    df = pd.DataFrame({"datalen": data[:, 0]-1, 'pixelscale': data[:, 1]-1, 'outcome': data[:, 2]})


    print(df.head(0))

    # kinda doesn't work - hey i did solve that w waterfall
    #pe.scatter(x=x,y=y, c=z)
    #pe.colorbar(cmap="turbo")

    #def make_mx_new(df, d_col="RSSI", t_col = "timestamp", x_col = "CH", xmax = 40, dtype='float16', lintime=True):

    vint = np.vectorize(int)
    pixelscales = vint(pixelscales*10)

    mx = chx.make_mx_new(df, d_col="outcome", t_col="datalen", x_col="pixelscale", xmax=max(pixelscales)+1) # hack lens+1 if issue
    datalens = np.array(datalens)
    pe.waterfall(mx, x_axis=pixelscales, yticks=datalens, cb_label="badness (blue ok, green bad, red autobad)")
    pe.xlabel("pixelscale*10")
    pe.ylabel("datalen")

    pe.show()


dataset1 = [({"datalen": 3, 'pixelscale': 0.1}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 3, 'pixelscale': 0.5}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 3, 'pixelscale': 0.8}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 3, 'pixelscale': 1}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 3, 'pixelscale': 1.1}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 3, 'pixelscale': 1.2}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 3, 'pixelscale': 1.3}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 3, 'pixelscale': 1.4}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 3, 'pixelscale': 1.5}, 'bad'),
({"datalen": 3, 'pixelscale': 1.6}, 'bad'),
({"datalen": 3, 'pixelscale': 1.7}, 'bad'),
({"datalen": 3, 'pixelscale': 1.8}, 'ok'),
({"datalen": 3, 'pixelscale': 1.9}, 'ok'),
({"datalen": 3, 'pixelscale': 2}, 'ok'),
({"datalen": 4, 'pixelscale': 0.1}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 4, 'pixelscale': 0.5}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 4, 'pixelscale': 0.8}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 4, 'pixelscale': 1}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 4, 'pixelscale': 1.1}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 4, 'pixelscale': 1.2}, 'bad'),
({"datalen": 4, 'pixelscale': 1.3}, 'bad'),
({"datalen": 4, 'pixelscale': 1.4}, 'bad'),
({"datalen": 4, 'pixelscale': 1.5}, 'ok'),
({"datalen": 4, 'pixelscale': 1.6}, 'ok'),
({"datalen": 4, 'pixelscale': 1.7}, 'ok'),
({"datalen": 4, 'pixelscale': 1.8}, 'bad'),
({"datalen": 4, 'pixelscale': 1.9}, 'bad'),
({"datalen": 4, 'pixelscale': 2}, 'bad'),
({"datalen": 5, 'pixelscale': 0.1}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 5, 'pixelscale': 0.5}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 5, 'pixelscale': 0.8}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 5, 'pixelscale': 1}, 'bad'),
({"datalen": 5, 'pixelscale': 1.1}, 'bad'),
({"datalen": 5, 'pixelscale': 1.2}, 'ok'),
({"datalen": 5, 'pixelscale': 1.3}, 'ok'),
({"datalen": 5, 'pixelscale': 1.4}, 'ok'),
({"datalen": 5, 'pixelscale': 1.5}, 'bad'),
({"datalen": 5, 'pixelscale': 1.6}, 'bad'),
({"datalen": 5, 'pixelscale': 1.7}, 'bad'),
({"datalen": 5, 'pixelscale': 1.8}, 'bad'),
({"datalen": 5, 'pixelscale': 1.9}, 'bad'),
({"datalen": 5, 'pixelscale': 2}, 'bad'),
({"datalen": 6, 'pixelscale': 0.1}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 6, 'pixelscale': 0.5}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 6, 'pixelscale': 0.8}, 'bad'),
({"datalen": 6, 'pixelscale': 1}, 'bad'),
({"datalen": 6, 'pixelscale': 1.1}, 'ok'),
({"datalen": 6, 'pixelscale': 1.2}, 'ok'),
({"datalen": 6, 'pixelscale': 1.3}, 'ok'),
({"datalen": 6, 'pixelscale': 1.4}, 'bad'),
({"datalen": 6, 'pixelscale': 1.5}, 'bad'),
({"datalen": 6, 'pixelscale': 1.6}, 'bad'),
({"datalen": 6, 'pixelscale': 1.7}, 'bad'),
({"datalen": 6, 'pixelscale': 1.8}, 'bad'),
({"datalen": 6, 'pixelscale': 1.9}, 'bad'),
({"datalen": 6, 'pixelscale': 2}, 'bad'),
({"datalen": 7, 'pixelscale': 0.1}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 7, 'pixelscale': 0.5}, 'autobad: autoscale fig (plt.tight_layout) failed - plot overflows'),
({"datalen": 7, 'pixelscale': 0.8}, 'bad'),
({"datalen": 7, 'pixelscale': 1}, 'ok'),
({"datalen": 7, 'pixelscale': 1.1}, 'ok'),
({"datalen": 7, 'pixelscale': 1.2}, 'ok'),
({"datalen": 7, 'pixelscale': 1.3}, 'ok'),
({"datalen": 7, 'pixelscale': 1.4}, 'bad'),
({"datalen": 7, 'pixelscale': 1.5}, 'bad'),
({"datalen": 7, 'pixelscale': 1.6}, 'bad'),
({"datalen": 7, 'pixelscale': 1.7}, 'bad'),
({"datalen": 7, 'pixelscale': 1.8}, 'bad'),
({"datalen": 7, 'pixelscale': 1.9}, 'bad'),
({"datalen": 7, 'pixelscale': 2}, 'bad')]

if __name__ == '__main__': # test if called as executable, not as library
    #txt = manshow_graph()
    #for line in txt:
    #    print(line)


    # make dummydata
    paramlist = [{"datalen":1, "pixelscale":2},{"datalen":3, "pixelscale":5}, {"datalen":1, "pixelscale":1}]
    results = ["OK", "Bad", "autobad"]
    pixelscales=[1,2,3,4,5]
    datalens=[1,2,3]
    evaluations = list(zip(paramlist, results))

    # hand over
    #plot_txt(evaluations, pixelscales=pixelscales, datalens=datalens)

    datalens = [3,4,5,6,7]
    pixelscales =  np.array(list(range(1,20,1)))/10
    #plot_txt(dataset1, pixelscales=pixelscales, datalens=datalens)



    dataset1_ok = [
    ({"datalen": 3, 'pixelscale': 1.8}, 'ok'),
    ({"datalen": 3, 'pixelscale': 1.9}, 'ok'),
    ({"datalen": 3, 'pixelscale': 2}, 'ok'),

    ({"datalen": 4, 'pixelscale': 1.5}, 'ok'),
    ({"datalen": 4, 'pixelscale': 1.6}, 'ok'),
    ({"datalen": 4, 'pixelscale': 1.7}, 'ok'),

    ({"datalen": 5, 'pixelscale': 1.2}, 'ok'),
    ({"datalen": 5, 'pixelscale': 1.3}, 'ok'),
    ({"datalen": 5, 'pixelscale': 1.4}, 'ok'),

    ({"datalen": 6, 'pixelscale': 1.1}, 'ok'),
    ({"datalen": 6, 'pixelscale': 1.2}, 'ok'),
    ({"datalen": 6, 'pixelscale': 1.3}, 'ok'),

    ({"datalen": 7, 'pixelscale': 1}, 'ok'),
    ({"datalen": 7, 'pixelscale': 1.1}, 'ok'),
    ({"datalen": 7, 'pixelscale': 1.2}, 'ok'),
    ({"datalen": 7, 'pixelscale': 1.3}, 'ok')
    ]

    x = [item[0]["pixelscale"] for item in dataset1_ok]
    y = [item[0]["datalen"] for item in dataset1_ok]

    pe = mi.myinkc()
    #k,d = LSQ(x,y)
    k,d = pe.LSQ(x,y)

    print(k,d) # -4.454382826475851 11.416815742397139 for dataset1_ok

    #pixelscales = # use from above
    dlen_opt = pixelscales*k + d

    pe.subplots()
    pe.plot(pixelscales, dlen_opt, label="optimal")
    pe.scatter(x, y, label="samples", color="orange")
    pe.xlabel("pixelscale")
    pe.ylabel("datalen")

    pe.show()