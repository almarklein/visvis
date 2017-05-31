# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import numpy as np

def statistics(data):
    """ Get StatData object for the given data.
    """
    return StatData(data)

class StatData:
    """ StatData(data)
    
    Get statistics on the given sequence of data. The data must be
    something that is accepted by np.array(). Any nonfinite data points
    (NaN, Inf, -Inf) are removed from the data.
    
    Allows easy calculation of statistics such as mean, std, median,
    any percentile, histogram data and kde's.
    
    This class was initially designed for the boxplot functionality.
    This interface was made public because it can be usefull to the
    generic user too.
    
    """
    
    def __init__(self, data):
        
        # Make numpy array, sort, make 1D, store
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        self._data = np.sort(data.ravel())
        
        # Remove invalids
        valid = np.isfinite(self._data)
        self._data = self._data[valid]
        
        # Calculate some stats
        self._mean = self._data.mean()
        self._std = self._data.std()
    
    def __repr__(self):
        return '<StatData object with %i elements>' % self.size
    
    def __str__(self):
        s = 'Summary of StatData object:\n'
        for key in ['size', 'dmin', 'dmax', 'drange', 'mean', 'std',
                    'Q1', 'Q2', 'Q3', 'IQR']:
            value = str(getattr(self, key))
            line = key.rjust(10) + ' = ' + value + '\n'
            s += line
        return s
    
    @property
    def size(self):
        """ Get the number of elements in the data.
        """
        return self._data.size
    
    @property
    def drange(self):
        """ Get the range of the data (max-min).
        """
        return float(self._data[-1] - self._data[0])
    
    @property
    def dmin(self):
        """ Get the minimum of the data.
        """
        return self._data[0]
    
    @property
    def dmax(self):
        """ Get the max of the data.
        """
        return self._data[-1]
    
    @property
    def mean(self):
        """ Get the mean of the data.
        """
        return self._mean
    
    @property
    def std(self):
        """ Get the standard deviation of the data.
        """
        return self._std
    
    @property
    def Q1(self):
        """ Get first quartile of the data (i.e. the 25th percentile).
        """
        return self.percentile(0.25)
    
    @property
    def Q2(self):
        """ Get second quartile of the data (i.e. the 50th percentile).
        This is the median.
        """
        return self.percentile(0.50)
    
    @property
    def median(self):
        """ Get the median. This is the same as Q2.
        """
        return self.percentile(0.50)
    
    @property
    def Q3(self):
        """ Get second quartile of the data (i.e. the 50th percentile).
        """
        return self.percentile(0.75)
    
    @property
    def IQR(self):
        """ Get the inter-quartile range; the range where 50% of the
        data is.
        """
        return self.percentile(0.75) - self.percentile(0.25)
    
    
    def percentile(self, per, interpolate=True):
        """ percentile(per, interpolate=True)
        
        Given a percentage (as a number between 0 and 1)
        return the value corresponding to that percentile.
        
        By default, the value is linearly interpolated if it does not
        fall exactly on an existing value.
        """
        
        # Calculate float index
        data = self._data
        i = (data.size-1) * float(per)
        
        # Sample the value
        if interpolate:
            # http://en.wikipedia.org/wiki/Percentile
            ik = int(i)
            ir = i - ik
            if ik >= data.size-1:
                return data[ik]
            else:
                return data[ik] + ir*(data[ik+1] - data[ik])
        else:
            i = int(round(i))
            return data[i]
    
    
    def histogram_np(self, nbins=None, drange=None, normed=False, weights=None):
        """"  histogram_np(self, nbins=None, range=None, normed=False, weights=None)
        
        Calculate the histogram of the data.
        
        If nbins is not given, a good value is chosen using
        the Freedman-Diaconis rule.
        Returns a 2-element tuple containing the bin centers and the
        counts.
        
        See also the kde() method.
        
        Parameters
        ----------
        nbins : int or sequence of scalars, optional
            If `bins` is an int, it defines the number of equal-width bins in
            the given range. If `bins` is a sequence, it defines
            the bin edges, including the rightmost edge, allowing for non-uniform
            bin widths. If not given, the optimal number of bins is calculated
            using the Freedman-Diaconis rule.
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
        
        """
        if nbins is None:
            nbins = self.best_number_of_bins()
        
        # Get histogram
        values, edges = np.histogram(self._data, nbins, drange, normed, weights)
        
        # The bins are the left bin edges, let's get the centers
        centers = np.empty(values.size, np.float32)
        for i in range(len(values)):
            centers[i] = (edges[i] + edges[i+1]) * 0.5
        
        # Done
        return centers, values
    
    
    def histogram(self, nbins=None):
        """  histogram(self, nbins=None)
        
        Calculate the (normalized) histogram of the data.
        
        If nbins is not given, a good value is chosen using
        the Freedman-Diaconis rule.
        
        See also the histogram_np() and kde() methods.
        
        """
        if nbins is None:
            nbins = self.best_number_of_bins()
        
        return self._kernel_density_estimate(nbins, [1])
    
    
    def kde(self, nbins=None, kernel=None):
        """  kde(self, nbins=None)
        
        Calculate the kernel density estimation of the data.
        
        If nbins is not given, a good value is chosen using
        the Freedman-Diaconis rule. If kernel is not given,
        a Gaussian kernel is used, with a sigma depending
        on nbins.
        
        """
        best_nbins = self.best_number_of_bins()
        
        if nbins is None:
            nbins = 4 * best_nbins
        if kernel is None:
            kernel = float(nbins) / best_nbins
        
        return self._kernel_density_estimate(nbins, kernel)
    
    
    def best_number_of_bins(self, minbins=8, maxbins=256):
        """ best_number_of_bins(minbins=8, maxbins=256)
        
        Calculates the best number of bins to make a histogram
        of this data, according to Freedman-Diaconis rule.
        
        """
        # Get data
        data = self._data
        
        # Get number of bins according to Freedman-Diaconis rule
        bin_size = 2 * self.IQR * data.size**(-1.0/3)
        nbins = self.drange / (bin_size+0.001)
        nbins = max(minbins, min(maxbins, int(nbins)))
        
        # Done
        return nbins
    
    
    def _kernel_density_estimate(self, n, kernel):
        """ kernel density estimate(n, kernel)
        """
        
        # Get data
        data = self._data
        
        # Get some statistics
        dmin, dmax, drange = self.dmin, self.dmax, self.drange
        if not drange:
            # A single value, or all values the same
            eps = 0.5
            dmin, dmax, drange = dmin-eps, dmax+eps, 2*eps
        
        # Construct kernel
        if isinstance(kernel, float):
            sigma = kernel
            ktail = int(sigma*3)
            kn = ktail*2 + 1
            t = np.arange(-kn/2.0+0.5, kn/2.0, 1.0, dtype=np.float64)
            k = np.exp(- t**2 / (2*sigma**2) )
        else:
            k = np.array(kernel, dtype='float64').ravel()
            ktail = int( k.size/2 )
        
        # nbins = 3
        #  ___  ___  ___
        # |   ||   ||   |
        # | | || | || | |
        #
        # [--- drange --]
        # [---] dbin
        
        # Get data "bins", these are the bin centers
        dbin = drange / n
        nbins = n + ktail * 2
        bins = (np.arange(nbins) - ktail + 0.5) * dbin + dmin
        
        # Normalize kernel
        k /= k.sum() * data.size * dbin
        
        # Splat the kernels in!
        # kde represents the counts for each bin.
        # xxi represents the data, but scaled to the bin indices. The elements
        # in xxi are sorted (because data is), and if data.size >> nbins
        # there are many equal values in a row. We make use of that to make
        # the bin splatting very efficient.
        kde = np.zeros_like(bins)
        xx = (data-dmin) * (1.0/dbin) # no +ktail here, no j-ktail at kernel index
        xxi = (xx).astype('int32')
        #
        # Init binary search
        step = max(1, int(data.size/n))
        i0, i1, i2 = 0, 0, step
        val = xxi[i0]
        totalSplats = 0
        #
        i2 = min(i2, xxi.size-1)
        while i1<i2:
            if xxi[i2] > val:
                if xxi[i2-1] == val:
                    # === found it!
                    # Splat kernel
                    nSplats = i2-i0
                    kde[val:val+k.size] += k * nSplats
                    totalSplats += nSplats
                    # Reset for next value
                    step = max(1, nSplats)
                    i0, i1, i2 = i2, i2, i2+step
                    val = xxi[i0]
                else:
                    # Too far
                    step = max(1, int(0.5*step))
                    i2 = i1 + step
            else:
                # Not far enough
                i1, i2 = i2, i2+step
            # Not beyond end!
            i2 = min(i2, xxi.size-1)
        # Wrap up
        if True:
            # Correct kernel (it might be at the way right edge
            if val >= n:
                val -= 1
            # Splat kernel
            nSplats = i2-i0+1
            kde[val:val+k.size] += k * nSplats
            totalSplats += nSplats
        
        # Check (should be equal)
        #print(totalSplats, xxi.size)
        
        if False:
            # Analog algoritm, better readable perhaps, but much slower:
            for x in data:
                i = (x-dmin) * (1.0/dbin) + ktail
                i = int(round(i))
                for j in range(k.size):
                    kde[i+j-ktail] += k[j]
        
        # Done
        return bins, kde
