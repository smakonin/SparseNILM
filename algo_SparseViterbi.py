#
# Alogirhtm/Module: the sparse Viterbi alorithm (algo_SparseViterbi.py)
# Copyright (C) 2013-2015 Stephen Makonin. All Right Reserved.
#

def dict_argmax(d):
    m_idx = m_val = 0
    
    for (idx, val) in d.items():
        if val > m_val:
            m_val = val
            m_idx = idx

    return (m_val, m_idx)

def disagg_algo(hmm, y):    
    cdone = [0, 0]
    ctotal = [hmm.K, hmm.K * hmm.K]
    
    P0 = hmm.P0
    A = hmm.A
    B = hmm.B
    Pt = [{}, {}]
    
    for (j, p_b) in B[y[0]]:
        if P0[j] == 0:
            continue        
        Pt[0][j] = P0[j] * p_b
        cdone[0] += 1
    
    for (j, p_b) in B[y[1]]:
        for (i, p_a) in A[j]:
            if i not in Pt[0]:
                continue

            p = Pt[0][i] * p_a * p_b
            cdone[1] += 1
            if j not in Pt[1] or p >= Pt[1][j]:
                Pt[1][j] = p

    return dict_argmax(Pt[1]) + tuple([Pt[1]]) + (cdone, ctotal)
