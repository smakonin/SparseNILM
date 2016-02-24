#
# Library/Module: empirical probability mass functions (PMF) (libPMF.py)
# Copyright (C) 2013-2015 Stephen Makonin. All Right Reserved.
#
 
class EmpiricalPMF:
    """A empirical probability mass function (PMF)."""

    label = ''         # Textually label your PMF.
    maxobs = 0         # The maximum obs value.
    numobs = 0         # The number of obs used for creation.
    histogram = []     # PMF observations counts.
    norm_hist = []     # The normalized histogram.
    bin_count = 0      # Number of bins.

    quantization = []  # The bin each PMF value is in.
    bin_peaks = []     # The peak in each bin.
    bins = []          # The observations count in each bin
    norm_bins = []     # The normalized bins

    def __init__(self, label, maxobs, priors, verbose=True):
        self.label = label
        self.maxobs = int(maxobs)
        self.numobs = len(priors)
        self.histogram = [0] * self.maxobs
        self.norm_hist = [0] * self.maxobs
        self.bin_count = 0
        
        for val in priors:
            self.histogram[val] += 1

        for i in range(self.maxobs):
            self.norm_hist[i] = self.histogram[i] / self.numobs
            
        #for printout only
        if verbose:
            maxval = 0
            for n in range(self.maxobs - 1, 0, -1):
                if self.histogram[n] > 1:
                    maxval = n + 1
                    break
            print('\tPMF for ' + label + ':', self.histogram[:maxval])

    def quantize(self, maxbins, epsilon, verbose=True):
        """Quantize the PMF histogram into bins."""
                
        if verbose: print('\tQuantize PMF:', self.label, end=', ')
        compare = lambda a, b: (a > b) - (a < b)
        element0 = self.histogram[0]
        self.histogram[0] = 0
        e = 0.0
        bins = maxbins + 1
        while bins > maxbins:
            e += epsilon
            bins = 1
            bin = 1

            self.quantization = [0] * self.maxobs
            self.bin_peaks = [0]
            switch = '-'

            for i in range(1, self.maxobs - 1):
                left = compare(self.histogram[i], self.histogram[i - 1])
                right = compare(self.histogram[i + 1], self.histogram[i])
                if left > 0 and right < 0 and switch == '-' and self.norm_hist[i] > e:
                    bins += 1
                    self.bin_peaks.append(i)
                    switch = '+'

                if left < 0 and (right > 0 or right == 0) and switch == '+':
                    if bin < bins: bin += 1
                    switch = '-'

                self.quantization[i] = bin
            self.quantization[-1] = self.quantization[-2]
            
            bin = bins - 1
            self.quantization = [bin if i >= bins else i for i in self.quantization]
            
        if verbose: print(('epsilon = {0:.' + str(len(str(epsilon)[2:])) + 'f}').format(e))
        self.histogram[0] = element0
        self.bin_count = bins
        
        self.bins = [0 for i in range(self.bin_count)]
        for i in range(self.maxobs):
            self.bins[self.quantization[i]] += self.histogram[i]

        self.norm_bins = [0 for i in range(self.bin_count)]
        for i in range(self.bin_count):
            self.norm_bins[i] = self.bins[i] / sum(self.histogram)

            first = self.quantization.index(i)
            last = self.maxobs - self.quantization[::-1].index(i) - 1
            if verbose: print('\t\tS%d: %5d:%5d, peak=%5d, %7d |t|' % (i, first, last, self.bin_peaks[i], self.bins[i]))
