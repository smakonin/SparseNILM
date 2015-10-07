#
# Library/Module: functions for load various datasets (libDataLoaders.py)
# Copyright (C) 2013-2015 Stephen Makonin. All Right Reserved.
#

import pandas

def AMPds_r1(filename, ids, precision, denoised=False, verbose=True):
    """Loaders for the AMPds Release 1 dataset."""
    
    timestamp_col = 'TimeStamp'
    agg_meter_col = 'WHE'
    unmetered_col = 'UNE'
    
    if verbose: print('Loading AMPds R1 dataset at %s...' % filename)
    df = pandas.read_csv(filename)
    
    if verbose: print('\tSetting timestamp column %s as index.' % timestamp_col)
    df = df.set_index(timestamp_col)
    
    if verbose: print('\tModfity data with precision %d then convert to int...' % precision)
    for col in list(df):
        df[col] = df[col] * precision
        df[col] = df[col].astype(int)

    cols = ids[:]
    if unmetered_col in cols:
        cols.remove(unmetered_col)
        if verbose: print('\tNoise will modelled as %s.' % unmetered_col)
        
    if verbose: print('\tKeeping only columns %s.' % str(cols))    
    df = df[[agg_meter_col] + cols]
    
    if denoised:
        if verbose: print('\tDenoising aggregate meter column %s.' % agg_meter_col)
        df[agg_meter_col] = df[cols].sum(axis=1)
    
    if verbose: print('\tCalculating unmetered column %s.' % unmetered_col)
    df[unmetered_col] = df[agg_meter_col] - df[cols].sum(axis=1)
    df.loc[df[unmetered_col] < 0] = 0

    return df    


def REDD_lo(filename, ids, precision, denoised=False, verbose=True):
    """Loaders for the AMPds Release 1 dataset."""
    
    timestamp_col = 'TimeStamp'
    agg_meter_col = 'MAIN'
    unmetered_col = 'DIFF'
        
    if verbose: print('Loading REDD Low Res dataset at %s...' % filename)
    df = pandas.read_csv(filename)

    if verbose: print('\tSetting timestamp column %s as index.' % timestamp_col)
    df = df.set_index(timestamp_col)

    cols = ids[:]
    if unmetered_col in cols:
        cols.remove(unmetered_col)
        if verbose: print('\tNoise will modelled as %s.' % unmetered_col)
        
    if verbose: print('\tKeeping only columns %s.' % str(cols))    
    df = df[[agg_meter_col] + cols]
    
    if denoised:
        if verbose: print('\tDenoising aggregate meter column %s.' % agg_meter_col)
        df[agg_meter_col] = df[cols].sum(axis=1)
    
    if verbose: print('\tCalculating unmetered column %s.' % unmetered_col)
    df[unmetered_col] = df[agg_meter_col] - df[cols].sum(axis=1)
    df.loc[df[unmetered_col] < 0] = 0

    return df  
        
def dataset_loader(filename, ids, precision, denoised=False, verbose=True):
    """A generic loader that (based in keyword in name) will use the correct loader to load dataset."""
    
    df = None
    if 'AMPds' in filename:
        df = AMPds_r1(filename, ids, precision, denoised, verbose)
    elif 'REDD' in filename:
        df = REDD_lo(filename, ids, precision, denoised, verbose)
    else:
        print("EORROR: Do not know how to load dataset!")
        exit(1)
        
    return df