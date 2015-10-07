#!/usr/bin/env python3
#
# Test a disaggreagation algorithm (test_Algorithm.py)
# Copyright (C) 2013-2015 Stephen Makonin. All Right Reserved.
#

import sys, json
from statistics import mean
from time import time
from datetime import datetime
from libDataLoaders import dataset_loader
from libFolding import Folding
from libSSHMM import SuperStateHMM
from libAccuracy import Accuracy


print()
print('----------------------------------------------------------------------------------------------------------------')
print('Test & Evaluate the Sparse Viterbi Algorithm with Saved SSHMMs  --  Copyright (C) 2013-2015, by Stephen Makonin.')
print('----------------------------------------------------------------------------------------------------------------')
print()
print('Start Time = ', datetime.now(), '(local time)')
print()

if len(sys.argv) != 9:
    print()
    print('USAGE: %s [test id] [modeldb] [dataset] [precision] [measure] [denoised] [limit] [algo name]' % (sys.argv[0]))
    print()
    print('       [test id]       - the seting ID.')
    print('       [modeldb]       - file name of model (omit file ext).')
    print('       [dataset]       - file name of dataset to use (omit file ext).')
    print('       [precision]     - number; e.g. 10 would convert A to dA.')
    print('       [measure]       - the measurement, e.g. A for current')    
    print('       [denoised]      - denoised aggregate reads, else noisy.')
    print('       [limit]         - a number to limit the amout of test, else use all.')
    print('       [algo name]     - specifiy the disaggregation algorithm to use.')
    print()
    exit(1)

print()
print('Parameters:', sys.argv[1:])
(test_id, modeldb, dataset, precision, measure, denoised, limit, algo_name) = sys.argv[1:]
precision = float(precision)
denoised = denoised == 'denoised'
limit = limit.lower()
if limit.isdigit():
    limit = int(limit)
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
indv_tm_sum = 0.0
indv_count = 0
y_noise = 0.0
y_total = 0.0
calc_done = [0,0]
calc_total = [0,0]
unexpected_event = 0
adapted_event = 0
adapted_errors = 0
multi_switches_count = 0

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
    pbar = ''
    pbar_incro = len(testing) // 20
    for i in range(1, len(obs)):
        multi_switches_count += (sum([i != j for (i, j) in list(zip(hidden[i - 1], hidden[i]))]) > 1)
        
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

        calc_done[0] += cdone[0]
        calc_done[1] += cdone[1]
        calc_total[0] += ctotal[0]
        calc_total[1] += ctotal[1]
        
        if p == 0.0:
            unexpected_event += 1
            
        indv_tm_sum += elapsed
        indv_count += 1
        
        y_noise += round(y1 - sum(y_true), 1)
        y_total += y1
        
        if not i % pbar_incro or i == 1:
            pbar += '=' #if i > 1 else ''
            disagg_rate = float(indv_tm_sum) / float(indv_count)
            print('\r\tCompleted %2d/%2d: [%-20s], Disagg rate: %12.6f sec/sample ' % (fold + 1, folds.folds, pbar[:20], disagg_rate), end='', flush=True)
            sys.stdout.flush()

        if limit != 'all' and i >= limit:
            print('\n\n *** LIMIT SET: Only testing %d obs. Testing ends now!' % limit)
            break;
                
    test_times.append((time() - tm_start) / 60)

    if limit != 'all' and i >= limit:
        break;

print()
print()
print('Evaluation and accuracy testing complete:')
disagg_rate = indv_tm_sum / indv_count
print('\tTest Time was', round(sum(test_times), 2), ' min (avg ', round(sum(test_times) / len(test_times), 2), ' min/fold).')
if calc_total[0] > 0 and calc_total[1] > 0:
    print('\tOptimization (Time) - Viterbi Part 1:',  round((calc_total[0] - calc_done[0]) / calc_total[0] * 100, 2), '% saved, ', format(calc_done[0], ',d'), 'calculations (average', round(calc_done[0] / indv_count, 1), 'calculations each time)')
    print('\tOptimization (Time) - Viterbi Part 2:',  round((calc_total[1] - calc_done[1]) / calc_total[1] * 100, 2), '% saved, ', format(calc_done[1], ',d'), 'calculations (average', round(calc_done[1] / indv_count, 1), 'calculations each time)')
else:
    print('\tOptimization (Time): NOT BEING TRACKED!')
print('\tUnexpected events =', unexpected_event, ', Multiple switch events =', multi_switches_count, ', Adapted events =', adapted_event, '(errors =', adapted_errors, ')')

acc.print(test_id, labels, measure)

report = []
report.append(['Test ID', test_id])
report.append(['Run Date', datetime.now()])
report.append(['Dataset', dataset])
report.append(['Precision', precision])
report.append(['Denoised?', denoised])
report.append(['Model Noise?', ('UNE' in labels)])
report.append(['Limit', limit])
report.append(['Algorithm', algo_name])
report.append(['Folds', folds.folds])
report.append(['Measure', measure])
report.append(['Tests', indv_count])
report.append(['Total Calc Vp1', calc_total[0]])
report.append(['Actual Calc Vp1', calc_done[0]])
report.append(['Total Calc Vp2', calc_total[1]])
report.append(['Actual Calc Vp2', calc_done[1]])
report.append(['Test Time', round(sum(test_times), 2)])
report.append(['Avg Time/Fold', round(sum(test_times) / len(test_times), 2)])
report.append(['Disagg Time', '{0:.10f}'.format(disagg_rate)])
report.append(['Unexpected', unexpected_event])
report.append(['Adapted', adapted_event])
report.append(['Adapted Errors', adapted_errors])
report.append(['Mult-Switches', multi_switches_count])
report.append(['Noise', round(y_noise / y_total, 4)])

print()
print('-------------------------------- CSV REPORTING --------------------------------')
print()
print(','.join([c[0] for c in report]))
print(','.join([str(c[1]) for c in report]))
print()
(acc_hdr, acc_det) = acc.csv(test_id, labels, measure)
print(acc_hdr)
print(acc_det)
print()
print('-------------------------------- ------------- --------------------------------')

print()
print('End Time = ', datetime.now(), '(local time)')
print()
print('DONE!!!')
print()
