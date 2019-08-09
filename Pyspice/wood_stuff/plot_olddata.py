"""
Note that sharex does not work for pickle.load.
If you zoom on the top graph, the other graphs do zoom, too, but only by means
of compressing their x-axis in the region of the zoom (not very useful).  Zooming on the non-top
sub-plots acts as an individual zoom.  I think this is a bug.

"""
import matplotlib.pyplot as plt
import pickle

with open('myplot.pkl','rb') as fid:
    pickle.load(fid)

plt.show()
