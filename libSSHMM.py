#
# Library/Module: super-state hidden Markov models (SSHMM) (libSSHMM.py)
# Copyright (C) 2013-2015 Stephen Makonin. All Right Reserved.
#

import sys, json, numpy
from functools import reduce

def product(a):
    """Calculate the product of a list."""
    return reduce(lambda x, y: x * y, a, 1)  

def frange(x, max, jump):
    """Like range() but for floats."""
    while round(x, len(str(jump)[2:])) < max:
        yield round(x, len(str(jump)[2:]))
        x += jump

def index_type(s):
    """Determine the numerical index type from string name."""
    index_types = ['none', 'hashing', 'full']
    
    try:
        i = index_types.index(s)
    except:
        raise RuntimeError('ERROR: indexing must be one of: none, hashing, or full')

    return i

def FNV_hash(d, key):
    """Use the FNV algorithm from http://isthe.com/chongo/tech/comp/fnv/"""
    prime = 0x01000193    # 32-bit
    #prime = 0x100000001B3 # 64-bit

    if d == 0: 
        d = prime
        
    if not isinstance(key, str):
        key = str(key)

    for c in key:
        octet = ord(c)
        d = ((d * prime) ^ octet) & 0xffffffff #FNV-1 algorithm
        #d = (d ^ (octet & 0xffffffff)) * prime #FNV-1a alternate algorithm

    return d

def rehash(kv):
    """Create a minimal perfect hash function/table based on the code by Steve Hanov."""    
    kv = list(filter(None.__ne__, kv))
    kvlen = len(kv)
    if(kvlen == 1):
        return ([0], kv)
    keys = tuple(zip(*kv))[0]
    values = kv

    maxtries = 1000
    maxexpand = 2
    repeat = True
    expand = 0
    
    while repeat: #and expand <= maxexpand:
        n = kvlen + expand
        repeat = False
        G = [0] * n
        V = [None] * n
        buckets = [[] for i in range(n)]
                
        for key in keys:
            buckets[FNV_hash(0, key) % n].append(key)
            
        buckets.sort(key=len, reverse=True)        
        for b in range(n):
            bucket = buckets[b]
            if len(bucket) <= 1: 
                break

            d = 1
            item = 0
            slots = []
            while item < len(bucket):
                slot = FNV_hash(d, bucket[item]) % n
                if V[slot] is not None or slot in slots:
                    d += 1
                    item = 0
                    slots = []
                    
                    if d > maxtries:
                        expand += 1
                        repeat = True
                        #print('Max tries reached, unable to split bucket', bucket)
                        #exit(1)
                        break
                else:
                    slots.append(slot)
                    item += 1

            if repeat:
                break
                
            G[FNV_hash(0, bucket[0]) % n] = d
            for i in range(len(bucket)):
                V[slots[i]] = values[keys.index(bucket[i])]

        if repeat:
            continue

        freelist = []
        for i in range(n): 
            if V[i] == None: 
                freelist.append(i)

        for b in range(b, n):
            bucket = buckets[b]
            if len(bucket) == 0: 
                break
            slot = freelist.pop()
            G[FNV_hash(0, bucket[0]) % n] = -slot - 1 
            V[slot] = values[keys.index(bucket[0])]
        
    return (G, V)

def hash_lookup(G, V, key):
    """Lookup a value based on minimal perfect hash function/table based on the code by Steve Hanov."""
    
    if len(G) == 0:
        return (-1, (-1, None))

    if len(V) == 1:
        return (0, V[0])

    
    d = G[FNV_hash(0, key) % len(G)]
    
    if d < 0: 
        i = -d - 1
    else:
        i = FNV_hash(d, key) % len(V)
    
    return (i, V[i])

class CompressedVector:
    """A compressed (no zero) vector that is slim on memory, unlike dict."""
    
    __slots__ = ['name', 'length', 'indexing', 'keys', 'hash_table', 'values', 'normalized']

    def __init__(self, name, length, indexing):
        self.name = name                     # The vector name
        self.length = length                 # The lenght of the uncolpressed vector.
        self.indexing = index_type(indexing) # Type of indexing to use 'none'=0,'hashed'=1,'full'=2
        self.keys = []                       # The column keys for the column vector.
        self.hash_table = []                 # The hash table for fast lookups
        self.values = []                     # The values for the given key in keys.
        self.normalized = False              # Is the Vector normalized?        

        if self.indexing == 2:
            self.values = [None] * self.length
        
    def __getitem__(self, key):
        if self.indexing == 0:
            try:
                i = self.keys.index(key)
                value = self.values[i]
            except:
                value = 0
        elif self.indexing == 1:
            (i, value) = hash_lookup(self.hash_table, self.values, key)
            if value is None:
               value = (key, 0)
            (k, value) = value
            if k != key:
                value = 0
        elif self.indexing == 2:
            value = self.values[key]
        
        return value
            
    def __setitem__(self, key, value):
        if self.indexing == 0:
            try:
                i = self.keys.index(key)
                self.values[i] = value
            except:
                self.keys.append(col)
                self.values.append(value)
        elif self.indexing == 1:
            (i, v) = hash_lookup(self.hash_table, self.values, key)
            if v is None:
                k = -1
            else:
                (k, v) = v
            if k == key:
                self.values[i] = (key, value)
            else:
                self.values.append((key, value))
                (self.hash_table, self.values) = rehash(self.values)
        elif self.indexing == 2:
                self.values[key] = value
            
    def incro(self, i):
        self[i] += 1

    def normalize(self):
        if self.normalized:
            return
        
        if self.indexing == 1:
            t = sum(list(zip(*self.values))[1])
        else:
            t = sum(self.values)

        for i in range(len(self.values)):
            if self.indexing == 1:
                (k, v) = self.values[i]
                self.values[i] = (k, v / t)
            else:
                self.values[i] /= t
        self.normalized = True

    def __iter__(self):
        for i in self.values:
            if i is None:
                continue
            yield tuple(i)

    def bytes(self):
        return sys.getsizeof(self) + sys.getsizeof(self.keys) + sys.getsizeof(self.hash_table) + sys.getsizeof(self.values)

    def size(self):
        return self.length
        
    def nonzero(self):
        return len(self.values)
        
    def sparsity(self):
        return round(1.0 - self.nonzero() / self.size(), 4)      

    def _asdict(self):
        """Convert all object properties to a dict."""
        
        d = {}
        d.update(name = self.name)        
        d.update(length = self.length)
        d.update(indexing = self.indexing)
        d.update(keys = self.keys)
        d.update(hash_table = self.hash_table)
        d.update(values = self.values)        
        d.update(normalized = self.normalized)        
        return(d)

    def _fromdict(self, d):
        """From a dict set all object properties."""
                
        self.name = d['name']
        self.length = d['length']
        self.indexing = d['indexing']
        self.keys = d['keys']
        self.hash_table = d['hash_table']
        self.values = d['values']
        self.normalized = d['normalized']
         
               
class CompressedMatrix:
    """A column compressed (no zero) or matrix that is slim on memory, unlike dict."""
    
    __slots__ = ['name', 'rows', 'cols', 'indexing', 'keys', 'hash_table', 'vectors', 'rowtl', 'normalized']
    
    def __init__(self, name, rows, cols, indexing):
        self.name = name                      # The matrix name
        self.rows = rows                      # The number of rows
        self.cols = cols                      # The number of columns
        self.indexing = index_type(indexing)  # Type of indexing to use 'none'=0,'hashed'=1,'full'=2
        self.keys = []                        # The column keys for the column vector.
        self.hash_table = []                  # The hash table for fast lookups
        self.vectors =[]                      # The vectors for the given key in keys.
        self.rowtl = {}                       # Store the row totals
        self.normalized = False               # Is the matix normalized?
        
        if self.indexing == 2:
            self.vectors = [None] * self.cols

    def __getitem__(self, key):
        if not (isinstance(key, (int, numpy.int32, numpy.int64)) or len(key) == 2):
            raise RuntimeError('ERROR: matrix key is either 1 or 2, e.g. m[row/col] or x[row, col]')

        if isinstance(key, (int, numpy.int32, numpy.int64)):
            row = None
            col = key
            value = []
        else:
            row = key[0]
            col = key[1]
            value = 0

        if self.indexing == 0:
            try:
                i = self.keys.index(col)
                vector = self.vectors[i]
            except:
                pass
        elif self.indexing == 1:
            (i, vector) = hash_lookup(self.hash_table, self.vectors, col)
            if vector is not None:
                (k, vector) = vector
                if k != col:
                    vector = None
        elif self.indexing == 2:
            vector = self.vectors[col]
        
        if vector is not None and row is None:
            value = vector.__iter__()
        elif vector is not None:
            value = vector[row]
                    
        return value
            
    def __setitem__(self, key, value):
        if len(key) != 2:
            raise RuntimeError('ERROR: matrix key is 2, e.g. x[row, col] = x')

        row = key[0]
        col = key[1]
            
        if self.indexing == 0:
            try:
                i = self.keys.index(col)
                self.vectors[i][row] = value
            except:            
                self.keys.append(col)
                self.vectors.append(CompressedVector(self.name + '.c' + str(col), self.rows, 'none'))
                self.vectors[-1][row] = value
        elif self.indexing == 1:
            (i, vector) = hash_lookup(self.hash_table, self.vectors, col)
            if vector is None:
                k = -1
            else:
                (k, vector) = vector
            if k != col:
                vector = CompressedVector(self.name + '.c' + str(col), self.rows, 'hashing')
                self.vectors.append((col, vector))
                (self.hash_table, self.vectors) = rehash(self.vectors)
            vector[row] = value
        elif self.indexing == 2:
            try:
                self.vectors[col][row] = value
            except:            
                self.vectors[col] = CompressedVector(self.name + '.c' + str(col), self.rows, 'hashing')
                self.vectors[col][row] = value
        
    def incro(self, row, col):
        self[row,col] += 1
        try:
            self.rowtl[row] += 1
        except:
            self.rowtl[row] = 1

    def incro_if0rowtl(self, row, col):
        if row not in self.rowtl:
            self[row,col] = 1.0

    def normalize(self, keep_rowtl=False):
        if self.normalized:
            return

        for vector in self.vectors:
            if vector is None:
                continue
            if self.indexing == 1:
                (k, vector) = vector
                
            for j in range(len(vector.values)):
                if self.indexing == 0:
                    v = vector.values[j]
                    i = vector.keys[j]
                    t = self.rowtl[i]
                    vector.values[j] = v / t
                elif self.indexing == 1 or self.indexing == 2:
                    if vector.values[j] is None:
                        continue
                    (k, v) = vector.values[j]
                    t = self.rowtl[k]
                    vector.values[j] = (k, v / t)
            vector.normalized = True

        if not keep_rowtl:
            self.rowtl = None    
        self.normalized = True
            
    def bytes(self):
        b = sys.getsizeof(self) + sys.getsizeof(self.keys) + sys.getsizeof(self.hash_table)
        for vector in self.vectors:
            if vector is None:
                continue
            if self.indexing == 1:
                (k, vector) = vector
            b += vector.size()
        return b       

    def size(self):
        return self.rows * self.cols
        
    def nonzero(self):
        c = 0
        for vector in self.vectors:
            if vector is None:
                continue
            if self.indexing == 1:
                (k, vector) = vector
            c += vector.nonzero()
        return c       
        
    def sparsity(self):
        return round(1.0 - self.nonzero() / self.size(), 4)    

    def _asdict(self):
        """Convert all object properties to a dict."""
        
        d = {}
        d.update(name = self.name)        
        d.update(rows = self.rows)
        d.update(cols = self.cols)
        d.update(indexing = self.indexing)
        d.update(keys = self.keys)
        d.update(hash_table = self.hash_table)
        d.update(vectors = self.vectors)        
        d.update(rowtl = self.rowtl)        
        d.update(normalized = self.normalized)        
        return(d)

    def _fromdict(self, d):
        """From a dict set all object properties."""
        
        self.name = d['name']
        self.rows = d['rows']
        self.cols = d['cols']
        self.indexing = d['indexing']
        self.keys = d['keys']
        self.hash_table = d['hash_table']  
              
        self.vectors = []
        for dd in d['vectors']:
            if dd is None:
                self.vectors.append(None)
                continue
            if self.indexing == 1:
                (k, dd) = dd

            d = CompressedVector(self.name + '.c', 0, 'hashing')
            d._fromdict(dd)

            if self.indexing == 0 or self.indexing == 2:
                self.vectors.append(d)
            elif self.indexing == 1:
                self.vectors.append((k, d))
        
        self.rowtl = d['rowtl']
        self.normalized = d['normalized']

class SuperStateHMM:
    """A (shared memory multiprocessing) super-state hidden Markov models (SSHMM)."""
    
    M = 0              # The number of finite-state machine (FSM).
    labels = []        # The labels for each FSM.
    Km = []            # The number of states per FSM.
    bin_peaks = []     # The peak vlaue in a bin for each FSM.
    bin_obs = []       # Which values are in which bin for each FSM.
    K = 0              # The number of super-states.
    N = 0              # The number of possible observations/emmisions.
    O = []             # The observations lablels.

    P0 = None          # Compressed unsafe memory P0.
    A = None           # Compressed unsafe shared memory A.
    B = None           # Compressed unsafe shared memory B.

    def __init__(self, pmfs=[], obs_labels=[], verbose=True):
        if len(pmfs) == 0:
            return 
            
        self.M = len(pmfs)
        self.labels = [pmf.label for pmf in pmfs]
        self.Km = [pmf.bin_count for pmf in pmfs]
        self.bin_peaks = [pmf.bin_peaks for pmf in pmfs]
        self.bin_obs = [pmf.quantization for pmf in pmfs]
        self.K = product(self.Km)
        self.N = len(obs_labels)
        self.O = obs_labels

        if verbose: 
            print('\tK = %s super-states (a sum of %d states), Km = %s.' % (format(self.K, ',d'), sum(self.Km), str(self.Km)))
            print('\tM = %d with labels %s, N = %s (%s to %s).' % (self.M, str(self.labels), self.N, str(self.O[0]), str(self.O[-1])))

    def build(self, obs, hidden, verbose=True):
        if verbose: print('\tEnumerating hidden state events: P0, A, B', end='', flush=True)

        self.P0 = CompressedVector('P0', self.K, 'hashing')
        self.A = CompressedMatrix('A', self.K, self.K, 'hashing')
        self.B = CompressedMatrix('B', self.K, self.N, 'full')
        
        pbar_incro = len(obs) // 20
        k0 = self.entangle_k(hidden[0])
        for i in range(len(obs)):
            k1 = self.entangle_k(hidden[i])
            y1 = obs[i]
      
            self.P0.incro(k1)
            self.A.incro(k0,k1)
            self.B.incro(k1,y1)

            if verbose and not i % pbar_incro:
                print('.', end='', flush=True)
                sys.stdout.flush()


            k0 = k1
        if verbose: print()
        
        if verbose: print('\tNormalizing vector P0...')        
        self.P0.normalize()
        if verbose: print('\tNormalizing matrix A...')        
        self.A.normalize()        
        if verbose: print('\tNormalizing matrix B...')        
        self.B.normalize()

## Requires too much space, to to solve this algorithmically.
#
#        #for B every row must sum to 1.0
#        if verbose: print('\tMatrix B: adding sum to 1.0 for 0 rows', end=' ', flush=True)
#        pbar_incro = self.K // 20
#        for k1 in range(self.K):
#            y_est = self.y_estimate(self.detangle_k(k1))
#            self.B.incro_if0rowtl(k1, y_est)
#
#            if verbose and not k1 % pbar_incro:
#                print('.', end='', flush=True)
#                sys.stdout.flush()
#                
#        if verbose: print()
#        self.B.rowtl = None
                    
        if verbose:
            print('\tOptimization (Space) - Sparsity:')
            print('\t\tP0[K]:    %6s%% sparse, non-zero values = %16s /  %30s.' % (str(round(self.P0.sparsity() * 100, 2)), format(self.P0.nonzero(), ',d'), format(self.P0.size(), ',d')))
            print('\t\tA[K,K]:   %6s%% sparse, non-zero values = %16s /  %30s.' % (str(round(self.A.sparsity() * 100, 2)), format(self.A.nonzero(), ',d'), format(self.A.size(), ',d')))
            print('\t\tB[K,N]:   %6s%% sparse, non-zero values = %16s /  %30s.' % (str(round(self.B.sparsity() * 100, 2)), format(self.B.nonzero(), ',d'), format(self.B.size(), ',d')))
            
            print('\tMemory Storage Requirements for Model:')
            print('\t\tP0[K]:    %20s bytes.' % (format(self.P0.bytes(), ',d')))
            print('\t\tA[K,K]:   %20s bytes.' % (format(self.A.bytes(), ',d')))
            print('\t\tB[K,N]:   %20s bytes.' % (format(self.B.bytes(), ',d')))
            print('\t\tTOTAL---->%20s bytes.' % (format(self.P0.bytes() + self.A.bytes() + self.B.bytes(), ',d')))

    def make_shared(self, stats_only=False, verbose=True):
        """Create safe, shared memory, multiprocessing structures: P0, A, B."""
        pass
        
    def y_estimate(self, X, breakdown=False):
        """Estimate the observed y from a vecoter of FSM states."""

        if breakdown:
            return [self.bin_peaks[m][X[m]] for m in range(self.M)]
            
        return sum([self.bin_peaks[m][X[m]] for m in range(self.M)])

    def detangle_k(self, k):
        """Determine the FSM states from the super-state."""
        
        X = []
        j = k
        
        for m in range(self.M - 1):
            divisor = product(self.Km[m + 1:])
            X.append(j // divisor)
            j %= divisor
        X.append(j)  
        
        return X

    def obs_to_bins(self, X):
        """Determine FSM states for a list of FSM observations."""
        bins = []
        
        for m in range(self.M):
            if X[m] >= len(self.bin_obs[m]):
                bins.append(self.bin_obs[m][-1])
            else:
                bins.append(self.bin_obs[m][X[m]])
                
        return bins
        
    def entangle_k(self, X, obs=True):
        """Determine the super-state from the FSM states."""

        if obs:
            X = self.obs_to_bins(X)

        k = 0
        for m in range(self.M - 1):
            k += X[m] * product(self.Km[m + 1:])
        k += X[-1]
        
        return k

    def _asdict(self):
        """Convert all object properties to a dict."""
        
        d = {}
        
        d.update(B = self.B)
        d.update(A = self.A)
        d.update(P0 = self.P0)

        d.update(O = self.O)
        d.update(N = self.N)
        d.update(K = self.K)
        d.update(bin_obs = self.bin_obs)
        d.update(bin_peaks = self.bin_peaks)
        d.update(Km = self.Km)
        d.update(labels = self.labels)
        d.update(M = self.M)
        
        return(d)
            
    def _fromdict(self, d):
        """From a dict set all object properties."""
                
        self.M = d['M']
        self.labels = d['labels']
        self.Km = d['Km']
        self.bin_peaks = d['bin_peaks']
        self.bin_obs = d['bin_obs']
        self.K = d['K']
        self.N = d['N']
        self.O = d['O']

        self.P0 = CompressedVector('P0', 0, 'hashing')
        self.P0._fromdict(d['P0'])
        
        self.A = CompressedMatrix('A', 0, 0, 'hashing')
        self.A._fromdict(d['A'])
        
        self.B = CompressedMatrix('B', 0, 0, 'full')
        self.B._fromdict(d['B'])

