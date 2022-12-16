# some plot-checks for mailuefterl

from mailuefterl import *
import myink as mi
pe = mi.myinkc()


def availability_plottests():
    for plot_test in [True, False]:
        pe.subplots()    
        a = availability(range(-115,-10), plot_test=plot_test)
        pe.scatter(*a, color="blue")

        b = np.array(list(range(-100,-90))+ list(range(-70,-40)))
        a = availability(b, plot_test=plot_test)
        pe.scatter(*a, color="red")

        b = np.array(list(range(-110,-90)))
        a = availability(b, plot_test=plot_test)
        pe.scatter(*a, color="green")


def ml_hist_plottests():
    data = range(0,100)
    import matplotlib.pyplot as plt
    #raw_n, raw_bins = histogram(x=data)

    pc_n, pc_bins = histogram(x=data, percent=True, autorange=True)
    x, xbins, xlines = plt.hist(x=data, weights=np.ones(np.shape(data))/count_non_nan(data) )
    plt.close("all")

    #print({f"{raw_n=}"})
    print(f"{pc_n=}")
    print(f"{x=}")

"""
    pe.subplots()

    pe.plot(bin_to_xaxis(raw_bins), raw_n, label="raw")
    #pe.twiny()
    pe.plot(bin_to_xaxis(pc_bins), pc_n, label="percent")
    
    pe.legend()    
"""

#-#-# module test #-#-#
if __name__ == '__main__': # test if called as executable, not as library
    #availability_plottests()
    ml_hist_plottests()

    pe.show()
    
