#
# Library/Module: functions for load various datasets (libDataLoaders.py)
# Copyright (C) 2013-2015 Stephen Makonin. All Right Reserved.
#

import pandas

def AMPds_r2013(filename, ids, precision, denoised=False, verbose=True):
    """Loaders for the AMPds Release 2013 dataset."""
    
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

def AMPds_v2(filename, ids, precision, denoised=False, verbose=True):
    """Loaders for the AMPds Version 2 dataset."""
    
    timestamp_col = 'UNIX_TS'
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
    
def TEALD_power(filename, ids, precision, denoised=False, verbose=True):
    """Loaders for the TEALD dataset."""
    
    timestamp_col = 'unix_ts'
    agg_meter_col = 'mains'
    unmetered_col = 'noise'
    
    if verbose: print('Loading TEALD dataset file %s...' % filename)
    df = pandas.read_csv(filename)
    
    if verbose: print('\tSetting timestamp column %s as index.' % timestamp_col)
    df = df.set_index(timestamp_col)
    
    if verbose: print('\tRemoving loads...')
    rm_list = []
    for id in ids:
        if '-' in id:
            sub_id = id[1:]
            df.drop(sub_id, inplace=True, axis=1)
            rm_list.append(id)
    for rm_id in rm_list:
        ids.remove(rm_id)

    headers = list(df.columns.values)
    headers = headers[2:]
    df[agg_meter_col] = df[headers].sum(axis=1)

    if verbose: print('\tCombining L1 and L2 for double-pole loads...')
    for id in ids:
        if '+' in id:
            sub_ids = id.split('+')
            df[id] = 0
            for sub_id in sub_ids:
                df[id] += df[sub_id]
            df.drop(sub_ids, inplace=True, axis=1)
    
    cols = ids[:]
    if unmetered_col in cols:
        cols.remove(unmetered_col)
        if verbose: print('\tNoise will modelled as %s.' % unmetered_col)
        
    if verbose: print('\tKeeping only columns %s.' % str(cols))    
    df = df[[agg_meter_col] + cols]
    
    if denoised:
        if verbose: print('\tDenoising aggregate meter column %s.' % agg_meter_col)
        df[agg_meter_col] = df[cols].sum(axis=1)
    
    if verbose: print('\tModfity data with precision %d then convert to int...' % precision)
    for col in list(df):
        df[col] = df[col] * precision
        df[col] = df[col].astype(int)

    if verbose: print('\tCalculating unmetered column %s.' % unmetered_col)
    df[unmetered_col] = df[agg_meter_col] - df[cols].sum(axis=1)
    df.loc[df[unmetered_col] < 0] = 0

    return df   

def TEALD_power(filename, ids, precision, denoised=False, verbose=True):
    """Loaders for the BCH dataset."""
    
    timestamp_col = 'unix_ts'
    agg_meter_col = 'mains'
    unmetered_col = 'noise'
    
    if verbose: print('Loading BCH dataset file %s...' % filename)
    df = pandas.read_csv(filename)
    
    if verbose: print('\tSetting timestamp column %s as index.' % timestamp_col)
    df = df.set_index(timestamp_col)
    
    if verbose: print('\tRemoving loads...')
    rm_list = []
    for id in ids:
        if '-' in id:
            sub_id = id[1:]
            df.drop(sub_id, inplace=True, axis=1)
            rm_list.append(id)
    for rm_id in rm_list:
        ids.remove(rm_id)

    headers = list(df.columns.values)
    headers = headers[2:]
    df[agg_meter_col] = df[headers].sum(axis=1)

    if verbose: print('\tCombining L1 and L2 for double-pole loads...')
    for id in ids:
        if '+' in id:
            sub_ids = id.split('+')
            df[id] = 0
            for sub_id in sub_ids:
                df[id] += df[sub_id]
            df.drop(sub_ids, inplace=True, axis=1)
    
    cols = ids[:]
    if unmetered_col in cols:
        cols.remove(unmetered_col)
        if verbose: print('\tNoise will modelled as %s.' % unmetered_col)
        
    if verbose: print('\tKeeping only columns %s.' % str(cols))    
    df = df[[agg_meter_col] + cols]
    
    if denoised:
        if verbose: print('\tDenoising aggregate meter column %s.' % agg_meter_col)
        df[agg_meter_col] = df[cols].sum(axis=1)
    
    if verbose: print('\tModfity data with precision %d then convert to int...' % precision)
    for col in list(df):
        df[col] = df[col] * precision
        df[col] = df[col].astype(int)

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
    if 'AMPdsR1' in filename:
        df = AMPds_r2013(filename, ids, precision, denoised, verbose)
    elif 'AMPdsR2' in filename:
        df = AMPds_v2(filename, ids, precision, denoised, verbose)
    elif 'TEALD' in filename:
        df = TEALD_power(filename, ids, precision, denoised, verbose)
    elif 'REDD' in filename:
        df = REDD_lo(filename, ids, precision, denoised, verbose)
    elif 'BCH' in filename:
        df = bch(filename, ids, precision, denoised, verbose)
    else:
        print("ERROR: Do not know how to load dataset!")
        exit(1)
        
    return df