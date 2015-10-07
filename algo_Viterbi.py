#
# Alogirhtm/Module: the Viterbi alorithm (algo_Viterbi.py)
# Copyright (C) 2013-2015 Stephen Makonin. All Right Reserved.
#

def argmax(a):
    val = max(a)
    idx = a.index(val)
    return (val, idx)

def disagg_algo(hmm, y):
    cdone = [0, 0]
    ctotal = [hmm.K, hmm.K * hmm.K]

    P0 = hmm.P0
    A = hmm.A
    B = hmm.B
    Pt = [[0.0 for k in range(hmm.K)], [0.0 for k in range(hmm.K)]]
    
    for j in range(hmm.K):
        Pt[0][j] = hmm.P0[j] * hmm.B[j,y[0]]
        cdone[0] += 1
    
    for j in range(hmm.K):
        for i in range(hmm.K):
            p = Pt[0][i] * hmm.A[i,j] * hmm.B[j,y[1]]            
            cdone[1] += 1
            if p >= Pt[1][j]:
                Pt[1][j] = p

    return argmax(Pt[1]) + tuple([Pt[1]]) + (cdone, ctotal)
