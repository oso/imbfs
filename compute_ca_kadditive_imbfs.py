from __future__ import print_function
import bz2
import multiprocessing
import os
import pickle
import time
from utils import cpu_time
from utils import powerset
from mipkadditive import mbf_ca_kadditive

nprofiles_done = 0
variables = None
kadditivity = 1
pset = None
loss_avg = 0
loss_min = 2**8
loss_max = None
count_nmbfs = 0

def compute_nonkadditive_mbfs_cb(result):
    global nprofiles_done
    global loss_min
    global loss_max
    global loss_avg
    global count_nmbfs

    profile, bad_avg, bad_min, bad_max, nimbfs, nmbfs, t = result
    nprofiles_done += 1

    loss_min = min(loss_min, bad_min)
    loss_max = max(loss_max, bad_max)
    loss_avg += bad_avg * nmbfs
    count_nmbfs += nmbfs

    print("%d. Profile %s done! bad assignments, min: %d, max: %d, avg: %.02f "
          "(%d IMBFS, %d MBFS) (%.02f seconds)" % (nprofiles_done,
          str(profile), bad_min, bad_max, bad_avg, nimbfs, nmbfs, t))

def compute_ca_kadditive_mbfs(filepath):
    global variables
    global pset
    global kadditivity

    t1 = cpu_time()

    f = bz2.BZ2File(filepath, 'rb')
    mbfs = pickle.load(f)

    bad_avg = 0
    bad = {}
    for mbf, n in mbfs.items():
        bad_assign = mbf_ca_kadditive(mbf, kadditivity, variables, pset)
        bad[mbf] = bad_assign
        bad_avg += n * bad_assign

    bad_avg /= sum(mbfs.values())
    bad_min = min(bad.values())
    bad_max = max(bad.values())

    nimbfs = len(mbfs)
    nmbfs = sum(mbfs.values())

    f.close()

    t = cpu_time() - t1

    profile = os.path.splitext(os.path.basename(filepath))[0]
    profile = os.path.splitext(profile)[0]
    profile = tuple(map(int, profile.split("-")))

    return profile, bad_avg, bad_min, bad_max, nimbfs, nmbfs, t

def compute_ca_kadditive_imbfs(n, k, indir):
    global count
    global variables
    global pset
    global kadditivity

    indir = indir + "/" if indir is not None else None

    variables = frozenset([(i + 1) for i in range(n)])
    pset = set([frozenset(p) for p in powerset(variables)])

    kadditivity = int(k)

    t1 = time.time()

    print("Number of CPUs: %d" % multiprocessing.cpu_count())

    pool = multiprocessing.Pool()
    n = 0
    for f in os.listdir(indir):
        if f.endswith(".pkl.bz2") is False:
            continue

        pool.apply_async(compute_ca_kadditive_mbfs,
                         (indir + f,),
                         callback = compute_nonkadditive_mbfs_cb)

    pool.close()
    pool.join()

    print("0/1 loss min: %.02f (%03d %%)" % (loss_min,
                                            ((100 * loss_min) / len(pset))))
    print("0/1 loss max: %.02f (%03d %%)" % (loss_max,
                                            ((100 * loss_max) / len(pset))))
    print("0/1 loss avg: %.02f (%03d %%)" % ((loss_avg / count_nmbfs),
                                            (100 * (loss_avg) / len(pset) / count_nmbfs)))
    print("total time: %.02f seconds" % (time.time() - t1))

if __name__ == "__main__":
    import sys
    import multiprocessing

    if len(sys.argv) < 4:
        print("usage: %s n k indir" % sys.argv[0])
        sys.exit(1)

    compute_ca_kadditive_imbfs(int(sys.argv[1]), sys.argv[2], sys.argv[3])
