# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
import numpy as np

def kde(data, bins=None, kernel=None, **kwargs):
    """ kde(a, bins=None, range=None, **kwargs)
    
    Make a kernerl density estimate plot of the data. This is like a
    histogram, but produces a smoother result, thereby better represening
    the probability density function.
    
    See the vv.StatData for more statistics on data.
    
    Parameters
    ----------
    a : array_like
        The data to calculate the historgam of.
    bins : int (optional)
        The number of bins. If not given, the best number of bins is
        determined automatically using the Freedman-Diaconis rule.
    kernel : float or sequence (optional)
        The kernel to use for distributing the values. If a scalar is given,
        a Gaussian kernel with a sigma equal to the given number is used.
        If not given, the best kernel is chosen baded on the number of bins.
    kwargs : keyword arguments
        These are given to the plot function.
    
    """
    
    # Get stats
    from visvis.processing.statistics import StatData
    stats = StatData(data)
    
    # Get kde
    xx, values = stats.kde(bins, kernel)
    
    # Plot
    return vv.plot(xx, values, **kwargs)


if __name__ == '__main__':
    vv.clf()
    data = np.random.normal(7,2,size=(100,100))
    b = vv.kde(data, lc='r')
