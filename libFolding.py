#
# Library/Module: k-fold cross-validation (libFolding.py)
# Copyright (C) 2013-2015 Stephen Makonin. All Right Reserved.
#

import pandas

class Folding:
    """Manage data for k-fold cross-validation."""

    folds = 0        # Number of folds used.
    fold = 0         # The current fold.
    reverse = False  # Reverse the folds where 1/k is priors, not testing.
    data_size = 0    # Total rows in dataset.
    data = []        # The data used for training and testing.
    
    def __init__(self, data, folds=10, reverse=False, verbose=True):
        self.folds = folds
        self.fold = self.folds
        self.data_size = len(data)
        self.reverse = reverse
        self.verbose = verbose

        if self.verbose: print()
        
        if self.folds == 1:
            self.data = data[:]
            if self.verbose: print('Created 1 fold: %s.' % (self.data_size))
        else:
            fold_size = self.data_size // self.folds
            self.data = [data[i:i + fold_size] for i in range(0, self.data_size, fold_size)]            
            if len(self.data) > self.folds:
                self.data[-2] = pandas.concat(self.data[-2:])
                del self.data[-1]
        
            if self.verbose: print('Created %d folds: %s.' % (self.folds, str([len(d) for d in self.data])))

    def __iter__(self):
        self.fold = -1
        return self
        
    def __next__(self):
        self.fold += 1
        if self.fold == self.folds:
            raise StopIteration

        if self.verbose:
            print()
            print()
            print('************************ VALIDATION ROUND: %2d/%2d ************************' % (self.fold + 1, self.folds))
            print()
            print('Building priors and testing datasets...')

        priors = []
        testing = []        
        one = None
        many = []        
        if self.folds == 1:
            priors = self.data  
            testing = self.data  
        else:
            for f in range(self.folds):
                if f != self.fold:
                    many.append(self.data[f])
            many = pandas.concat(many)
            one = self.data[self.fold]

            if self.reverse:
                priors = one
                testing = many
            else:
                priors = many
                testing = one

            if self.verbose: print('\tLengths are: priors %d, testing %d.' % (len(priors), len(testing)))

        return (self.fold, priors, testing)
