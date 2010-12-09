# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
import numpy as np

def hist(data, bins=10, range=None, normed=False, weights=None, **kwargs):
    """ hist(a, bins=10, range=None, normed=False, weights=None, **kwargs)
    
    Make a histogram plot of the data. Uses np.histogram (new version) 
    internally. See its docs for more information. 
    
    Parameters
    ----------
    a : array_like
        The data to calculate the historgam of.
    bins : int or sequence of scalars, optional
        If `bins` is an int, it defines the number of equal-width bins in
        the given range (10, by default). If `bins` is a sequence, it defines
        the bin edges, including the rightmost edge, allowing for non-uniform
        bin widths.
    range : (float, float)
        The lower and upper range of the bins. If not provided, range is
        simply (a.min(), a.max()). Values outside the range are ignored. 
    normed : bool
        If False, the result will contain the number of samples in each bin. 
        If True, the result is the value of the probability *density* 
        function at the bin, normalized such that the *integral* over the 
        range is 1. Note that the sum of the histogram values will not be 
        equal to 1 unless bins of unity width are chosen; it is not a 
        probability *mass* function.
    weights : array_like
        An array of weights, of the same shape as `a`. Each value in `a` 
        only contributes its associated weight towards the bin count 
        (instead of 1). If `normed` is True, the weights are normalized, 
        so that the integral of the density over the range remains 1.     
    kwargs : keyword arguments
        These are given to the plot function.
    
    """
    
    # let numpy do the work
    if np.__version__ < '1.3':
        values, edges = np.histogram(data, bins, range, normed, weights, new=True)
    else:
        values, edges = np.histogram(data, bins, range, normed, weights)
    
    # the bins are the left bin edges, let's get the centers
    range = __builtins__['range']
    centers = np.empty(values.shape, np.float64)
    for i in range(len(values)):
        centers[i] = (edges[i] + edges[i+1]) * 0.5
    
    # plot
    return vv.plot(centers, values, **kwargs)
    
if __name__ == '__main__':
    data = np.random.normal(7,2,size=(100,100))
    hist(data)
