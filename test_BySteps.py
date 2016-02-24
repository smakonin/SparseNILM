#!/usr/bin/env python3
#
# Test running NILM and report stats each time (test_BySteps.py)
# Copyright (C) 2016 Stephen Makonin. All Right Reserved.
#

import sys, json
from statistics import mean
from time import time, sleep
from datetime import datetime
from libDataLoaders import dataset_loader
from libFolding import Folding
from libSSHMM import SuperStateHMM
from libAccuracy import Accuracy


print()
print('-----------------------------------------------------------------------------------------')
print('Test running NILM and report stats each time  --  Copyright (C) 2016, by Stephen Makonin.')
print('-----------------------------------------------------------------------------------------')
print()
print('Start Time = ', datetime.now(), '(local time)')
print()

if len(sys.argv) != 8:
    print()
    print('USAGE: %s [test id] [modeldb] [dataset] [precision] [measure] [denoised] [algo name]' % (sys.argv[0]))
    print()
    print('       [test id]       - the seting ID.')
    print('       [modeldb]       - file name of model (omit file ext).')
    print('       [dataset]       - file name of dataset to use (omit file ext).')
    print('       [precision]     - number; e.g. 10 would convert A to dA.')
    print('       [measure]       - the measurement, e.g. A for current')    
    print('       [denoised]      - denoised aggregate reads, else noisy.')
    print('       [algo name]     - specifiy the disaggregation algorithm to use.')
    print()
    exit(1)

print()
print('Parameters:', sys.argv[1:])
(test_id, modeldb, dataset, precision, measure, denoised, algo_name) = sys.argv[1:]
precision = float(precision)
denoised = denoised == 'denoised'
disagg_algo = getattr(__import__('algo_' + algo_name, fromlist=['disagg_algo']), 'disagg_algo')
print('Using disaggregation algorithm disagg_algo() from %s.' % ('algo_' + algo_name + '.py'))

datasets_dir = './datasets/%s.csv'
logs_dir = './logs/%s.log'
models_dir = './models/%s.json'

print()
print('Loading saved model %s from JSON storage (%s)...' % (modeldb, models_dir % modeldb))
fp = open(models_dir % modeldb, 'r')
jdata = json.load(fp)
fp.close()
folds = len(jdata)
print('\tModel set for %d-fold cross-validation.' % folds)
print('\tLoading JSON data into SSHMM objects...')
sshmms = []
for data in jdata:
    sshmm = SuperStateHMM()
    sshmm._fromdict(data)
    sshmms.append(sshmm)
del jdata
labels = sshmms[0].labels
print('\tModel lables are: ', labels)

print()
print('Testing %s algorithm load disagg...' % algo_name)
acc = Accuracy(len(labels), folds)
test_times = []

print()
folds = Folding(dataset_loader(datasets_dir % dataset, labels, precision, denoised), folds)
for (fold, priors, testing) in folds: 
    del priors
    tm_start = time()
    
    sshmm = sshmms[fold]
    obs_id = list(testing)[0]
    obs = list(testing[obs_id])
    hidden = [i for i in testing[labels].to_records(index=False)]
    
    print()
    print('Begin evaluation testing on observations, compare against ground truth...')
    print()

    for i in range(1, len(obs)):
        acc.reset()
                
        y0 = obs[i - 1]
        y1 = obs[i]
        
        start = time() 
        (p, k, Pt, cdone, ctotal) = disagg_algo(sshmm, [y0, y1])
        elapsed = (time() - start)

        s_est = sshmm.detangle_k(k)
        y_est = sshmm.y_estimate(s_est, breakdown=True)
        
        y_true = hidden[i]
        s_true = sshmm.obs_to_bins(y_true)

        acc.classification_result(fold, s_est, s_true, sshmm.Km)
        acc.measurement_result(fold, y_est, y_true)
        
        unseen = 'no'
        if p == 0.0:
            unseen = 'yes'
                    
        y_noise = round(y1 - sum(y_true), 1)
                
        fscore = acc.fs_fscore()
        estacc = acc.estacc()
        scp = sum([i != j for (i, j) in list(zip(hidden[i - 1], hidden[i]))])
        #print('Obs %5d%s | Δ %4d%s | Noise %3d%s | SCP %2d | Unseen? %-3s | FS-fscore %.4f | Est.Acc. %.4f | Time %7.3fms' % (y1, measure, y1 - y0, measure, y_noise, measure, scp, unseen, fscore, estacc, elapsed * 1000))
        print('Obs %5d%s Δ %4d%s | SCP %2d | FS-fscore %.4f | Est.Acc. %.4f | Time %7.3fms' % (y1, measure, y1 - y0, measure, scp, fscore, estacc, elapsed * 1000))
        sleep(1)
        
    test_times.append((time() - tm_start) / 60)

print('\tTest Time was', round(sum(test_times), 2), ' min (avg ', round(sum(test_times) / len(test_times), 2), ' min/fold).')
print()
print('End Time = ', datetime.now(), '(local time)')
print()
print('DONE!!!')
print()
