#
# Library/Module: track testing/evaluation accuracy and report measures (libAccuracy.py)
# Copyright (C) 2013-2015 Stephen Makonin. All Right Reserved.
#

from math import sqrt

def quotient(n, d):
    """A better quotient/divide function."""

    a = -1
    if n != 0 and d == 0:
        a = 0
    elif n == 0 and d == 0:
        a = 0
    else:
        a = float(n) / float(d)
    return a

def mean(a):
    """A better mean function."""
    return float(sum(a)) / float(len(a))

class Accuracy:
    """Track testing/evaluation accuracy and report measures."""

    items = 0             # Number of items to track accuracy for.
    folds = 0             # Number of folds used for testing/evaluation.
    trials = []           # Total numer of tests/evaluatins done per fold.

    count_inacc = []      # Numer of inaccurate classifications per fold per item.
    count_atp = []        # Numer of accurate portion of true-positives per fold per item.
    count_itp = []        # Numer of inaccurate portion of true-positives per fold per item.
    count_tp = []         # Numer of true-positives per fold per item.
    count_tn = []         # Numer of true-negatives per fold per item.
    count_fp = []         # Numer of false-positives per fold per item.
    count_fn = []         # Numer of false-negatives per fold per item.

    measure_est = []      # A measure of the estimate per fold per item.
    measure_truth = []    # A measure of the truth per fold per item.
    measure_diff = []     # A measure of diferent beteen estimate and truth per fold per item.
    measure_diff_sq = []  # The value of measure_diff squared per fold per item.
    measure_mean_abs = [] # A measure of mean absolute error per fold per item
    ovall_mape = 0        # A measure of mean absolute error per fold per item

    inacc            = lambda self, m = -1: round(mean(self.count_inacc[m]), 4) if m >= 0 else sum([self.inacc(i) for i in range(self.items)])
    atp              = lambda self, m = -1: int(mean(self.count_atp[m])) if m >= 0 else sum([self.atp(i) for i in range(self.items)])
    itp              = lambda self, m = -1: int(mean(self.count_itp[m])) if m >= 0 else sum([self.itp(i) for i in range(self.items)])
    tp               = lambda self, m = -1: int(mean(self.count_tp[m])) if m >= 0 else sum([self.tp(i) for i in range(self.items)])
    hit              = lambda self, m = -1: self.tp(m)
    tn               = lambda self, m = -1: int(mean(self.count_tn[m])) if m >= 0 else sum([self.tn(i) for i in range(self.items)])
    corr_reject      = lambda self, m = -1: self.tn(m)
    fp               = lambda self, m = -1: int(mean(self.count_fp[m])) if m >= 0 else sum([self.fp(i) for i in range(self.items)])
    false_alarm      = lambda self, m = -1: self.fp(m)
    typeI_error      = lambda self, m = -1: self.fp(m)
    fn               = lambda self, m = -1: int(mean(self.count_fn[m])) if m >= 0 else sum([self.fn(i) for i in range(self.items)])
    miss             = lambda self, m = -1: self.fn(m)
    typeII_error     = lambda self, m = -1: self.fn(m)
    correct          = lambda self, m = -1: self.tp(m) + self.tn(m)
    incorrect        = lambda self, m = -1: self.fp(m) + self.fn(m)
    tp_rate          = lambda self, m = -1: round(quotient(self.tp(m), self.tp(m) + self.fn(m)), 4)
    sensitivity      = lambda self, m = -1: self.tp_rate(m)
    recall           = lambda self, m = -1: self.tp_rate(m)
    hit_rate         = lambda self, m = -1: self.tp_rate(m)
    tn_rate          = lambda self, m = -1: round(quotient(self.tn(m), self.fp(m) + self.tn(m)), 4)
    specificity      = lambda self, m = -1: self.tn_rate(m)
    precision        = lambda self, m = -1: round(quotient(self.tp(m), self.tp(m) + self.fp(m)), 4)
    pos_predictive   = lambda self, m = -1: self.precision(m)
    neg_predictive   = lambda self, m = -1: round(quotient(self.tn(m), self.tn(m) + self.fn(m)), 4)
    fp_rate          = lambda self, m = -1: round(quotient(self.fp(m), self.fp(m) + self.tn(m)), 4)
    fall_out         = lambda self, m = -1: self.fp_rate(m)
    fn_rate          = lambda self, m = -1: round(quotient(self.fn(m), self.fn(m) + self.tp(m)), 4)
    miss_rate        = lambda self, m = -1: self.fn_rate(m)
    false_discovery  = lambda self, m = -1: round(quotient(self.fp(m), self.tp(m) + self.fp(m)), 4)
    accuracy         = lambda self, m = -1: round(quotient(self.correct(m), self.correct(m) + self.incorrect(m)), 4)
    fscore           = lambda self, m = -1: round(2 * quotient(self.precision(m) * self.recall(m), self.precision(m) + self.recall(m)), 4)
    matthews_correl  = lambda self, m = -1: round(quotient(self.tp(m) * self.tn(m) + self.fp(m) * self.fn(m), sqrt((self.tp(m) + self.fp(m)) * (self.tp(m) + self.fn(m)) * (self.tn(m) + self.fp(m)) * (self.tn(m) + self.fn(m)))), 4)
    informedness     = lambda self, m = -1: round(self.tp_rate(m) + self.tn_rate(m) - 1, 4)
    markedness       = lambda self, m = -1: round(self.pos_predictive(m) + self.neg_predictive(m) - 1, 4)
    nde              = lambda self, m = -1: round(quotient(abs(self.est(m) - self.truth(m)), self.truth(m)), 4)
    rmse             = lambda self, m = -1: round(sqrt(quotient(1, mean(self.trials)) * mean(self.measure_diff_sq[m])) if m >= 0 else sum([self.rmse(i) for i in range(self.items)]), 4)
    diff             = lambda self, m = -1: round(mean(self.measure_diff[m]) if m >= 0 else sum([self.diff(i) for i in range(self.items)]), 2)
    est              = lambda self, m = -1: round(mean(self.measure_est[m]) if m >= 0 else sum([self.est(i) for i in range(self.items)]), 2)
    truth            = lambda self, m = -1: round(mean(self.measure_truth[m]) if m >= 0 else sum([self.truth(i) for i in range(self.items)]), 2)
    kolter           = lambda self, m = -1: round(1 - quotient(self.diff(m), 2 * self.truth(m)), 4)

    m_precision      = lambda self, m = -1: round(quotient(self.atp(m), self.atp(m) + self.itp(m) + self.fp(m)), 4)
    m_recall         = lambda self, m = -1: round(quotient(self.atp(m), self.atp(m) + self.itp(m) + self.fn(m)), 4)
    m_fscore         = lambda self, m = -1: round(2 * quotient(self.m_precision(m) * self.m_recall(m), self.m_precision(m) + self.m_recall(m)), 4)

    fs_precision     = lambda self, m = -1: round(quotient(self.tp(m) - self.inacc(m), self.tp(m) + self.fp(m)), 4)
    fs_recall        = lambda self, m = -1: round(quotient(self.tp(m) - self.inacc(m), self.tp(m) + self.fn(m)), 4)
    fs_fscore        = lambda self, m = -1: round(2 * quotient(self.fs_precision(m) * self.fs_recall(m), self.fs_precision(m) + self.fs_recall(m)), 4)
    estacc           = lambda self, m = -1: round(1 - quotient(abs(self.est(m) - self.truth(m)), self.truth(m)), 4)

    est_percent      = lambda self, m: round(quotient(self.est(m), self.est()), 4)
    truth_percent    = lambda self, m: round(quotient(self.truth(m), self.truth()), 4)

    # measurement added for prediction accuracy
    mape             = lambda self, m = -1: round(quotient(sum(self.measure_mean_abs[m]), sum(self.trials)) if m >= 0 else quotient(self.ovall_mape, sum(self.trials)), 4)

    def __init__(self, items, folds):
        self.items = items
        self.folds = folds
        self.reset()

    def reset(self):
        self.trials = [0 for i in range(self.folds)]

        self.count_inacc = [[0 for s in range(self.folds)] for i in range(self.items)]
        self.count_atp = [[0 for s in range(self.folds)] for i in range(self.items)]
        self.count_itp = [[0 for s in range(self.folds)] for i in range(self.items)]
        self.count_tp = [[0 for s in range(self.folds)] for i in range(self.items)]
        self.count_tn = [[0 for s in range(self.folds)] for i in range(self.items)]
        self.count_fp = [[0 for s in range(self.folds)] for i in range(self.items)]
        self.count_fn = [[0 for s in range(self.folds)] for i in range(self.items)]

        self.measure_est = [[0 for s in range(self.folds)] for i in range(self.items)]
        self.measure_truth = [[0 for s in range(self.folds)] for i in range(self.items)]
        self.measure_diff = [[0 for s in range(self.folds)] for i in range(self.items)]
        self.measure_diff_sq = [[0 for s in range(self.folds)] for i in range(self.items)]
        self.measure_mean_abs = [[0 for s in range(self.folds)] for i in range(self.items)]
        self.ovall_mape = 0

    def classification_result(self, fold, est, truth, states):
        """Record the classification results of a test."""

        self.trials[fold] += 1

        for item in range(self.items):
            if est[item] > 0 and truth[item] > 0:
                self.count_inacc[item][fold] += float(abs(est[item] - truth[item])) / float(states[item])
                self.count_tp[item][fold] += 1
            elif est[item] == 0 and truth[item] == 0:
                self.count_tn[item][fold] += 1
            elif est[item] > 0 and truth[item] == 0:
                self.count_fp[item][fold] += 1
            elif est[item] == 0 and truth[item] > 0:
                self.count_fn[item][fold] += 1
            else:
                print("EORROR: impossible FS f-score case!")
                exit(1)

    def measurement_result(self, fold, est, truth):
        """Record the classification results of a test."""

        for item in range(self.items):
            diff = est[item] - truth[item]

            self.measure_est[item][fold] += est[item]
            self.measure_truth[item][fold] += truth[item]
            self.measure_diff[item][fold] += abs(diff)
            self.measure_diff_sq[item][fold] += diff ** 2

            rho = 0.2
            if est[item] > 0 and truth[item] > 0:
                prec_diff = abs(diff) / truth[item]
                self.measure_mean_abs[item][fold] += prec_diff
                self.ovall_mape += abs(sum(truth) - sum(est)) / sum(truth)

                if prec_diff <= rho:
                    self.count_atp[item][fold] += 1
                else:
                    self.count_itp[item][fold] += 1

    def csv(self, test_id, labels, measure):
        """Get the results and CSV data."""

        hdr = 'Test ID,Item,Correct,Incorrect,TP,Inacc,APT,ITP,TN,FP,FN,Basic Acc,Precision,Recall,F-Score,M Precision,M Recall,M F-Score,FS Precision,FS Recall,FS F-Score,RMSE,NDE,MAPE,Kolter,Est Acc,Estimated,Actual,Diff,Est of Total,Actual of Total'
        det = ''
        for i in range(-1, self.items):
            label = '*TL'
            if i > -1:
                label = labels[i]
            det += ','.join([str(v) for v in [test_id, label, self.correct(i), self.incorrect(i), self.tp(i), self.inacc(i), self.atp(i), self.itp(i), self.tn(i), self.fp(i), self.fn(i), self.accuracy(i), self.precision(i), self.recall(i), self.fscore(i), self.m_precision(i), self.m_recall(i), self.m_fscore(i), self.fs_precision(i), self.fs_recall(i), self.fs_fscore(i), self.rmse(i), self.nde(i), self.mape(i), self.kolter(i), self.estacc(i), self.est(i), self.truth(i), self.diff(i), self.est_percent(i), self.truth_percent(i)]]) + '\n'

        return (hdr, det)

    def print(self, test_id, labels, measure):
        """Print the a results report to the screen."""

        print()
        print()
        print('Classification & Esitmation Accuracies (Test %s):' % test_id)
        print()
        print('\tAccuracy     = %6.2f%% (%s incorrect tests)' % (self.accuracy() * 100, format(self.incorrect(), ',d')))
        print('\tPrecision    = %6.2f%%' % (self.precision() * 100))
        print('\tRecall       = %6.2f%%' % (self.recall() * 100))
        print('\tF-Score      = %6.2f%%' % (self.fscore() * 100))

        print()
        print('\tM Precision  = %6.2f%%' % (self.m_precision() * 100))
        print('\tM Recall     = %6.2f%%' % (self.m_recall() * 100))
        print('\tM F-Score    = %6.2f%%' % (self.m_fscore() * 100))

        print()
        print('\tFS Precision = %6.2f%%' % (self.fs_precision() * 100))
        print('\tFS Recall    = %6.2f%%' % (self.fs_recall() * 100))
        print('\tFS F-Score   = %6.2f%%' % (self.fs_fscore() * 100))
        print()
        print('\tNDE          = %6.2f%%' % (self.nde() * 100))
        print('\tMAPE         = %6.2f%%' % (self.mape() * 100))
        print('\tRMSE         = %6.2f' % (self.rmse()))
        print('\tEsitmation   = %6.2f%% (%s %s difference)' % (self.estacc() * 100, format(self.diff(), ',.1f'), measure))
        print()

        print('\t|----------|----------|---------|-----------|-----------|----------|-------------------------------|------------|-------------------|')
        print('\t|          |          |         |           |           |          | FINITE-STATE MODIFICATIONS:   |            | PRECENT OF TOTAL: |')
        print('\t| item ID  | ACCURACY |     NDE |    MAPE   |   F-SCORE | M-FSCORE | PRECISION |  RECALL | F-SCORE | ESITMATION |     EST |   TRUTH |')
        print('\t|----------|----------|---------|-----------|-----------|----------|-----------|---------|---------|------------|---------|---------|')
        for i in range(self.items):
            print('\t| %-8s |  %6.2f%% | %6.2f%% |  %7.2f%% |   %6.2f%% |  %6.2f%% |   %6.2f%% | %6.2f%% | %6.2f%% |   %7.2f%% | %6.2f%% | %6.2f%% |' % (labels[i], self.accuracy(i) * 100, self.nde(i) * 100, self.mape(i) * 100, self.fscore(i) * 100, self.m_fscore(i) * 100, self.fs_precision(i) * 100, self.fs_recall(i) * 100, self.fs_fscore(i) * 100, self.estacc(i) * 100, self.est_percent(i) * 100, self.truth_percent(i) * 100))
        print('\t|----------|----------|---------|-----------|-----------|----------|-----------|---------|---------|------------|=========|=========|')
        print('\t                                                                                                                | 100.00% | 100.00% |')
        print('\t                                                                                                                |---------|---------|')
        print()
