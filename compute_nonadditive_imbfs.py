from __future__ import print_function
import bz2
import multiprocessing
import os
import pickle
import time
from utils import cpu_time
from utils import powerset
from additive import mbf_is_additive

nprofiles_done = 0
total_mbfs_count = 0
total_imbfs_count = 0
outdir = None
variables = None
pset = None

def compute_nonadditive_mbfs_cb(result):
    global total_mbfs_count
    global total_imbfs_count
    global nprofiles_done

    profile, nmbfs, nimbfs, mbfs_count, imbfs_count, t = result
    nprofiles_done += 1
    total_imbfs_count += imbfs_count
    total_mbfs_count += mbfs_count

    print("%d. Profile %s done!\t%10d (/%d) non-additives iMBFs (%d/%d MBFS) "
          "found (%.02f seconds)" % (nprofiles_done, str(profile), imbfs_count,
          nimbfs, mbfs_count, nmbfs, t))

def compute_nonadditive_mbfs(filepath):
    global outdir
    global variables
    global pset

    t1 = cpu_time()

    f = bz2.BZ2File(filepath, 'rb')
    mbfs = pickle.load(f)

    mbfs_count = imbfs_count = 0
    nmbfs = nimbfs = 0
    imbfs = set()
    for mbf, n in mbfs.items():
        additive = mbf_is_additive(mbf, variables, pset)
        if additive is False:
            imbfs.add(mbf)
            imbfs_count += 1
            mbfs_count += n

        nimbfs += 1
        nmbfs += n

    f.close()

    t = cpu_time() - t1

    profile = os.path.splitext(os.path.basename(filepath))[0]
    profile = os.path.splitext(profile)[0]
    profile = tuple(map(int, profile.split("-")))

    if outdir is not None and len(imbfs) > 0:
        filenameout = "-".join(map(str, profile)) + ".pkl.bz2"
        fileout = bz2.BZ2File(outdir + filenameout, 'wb')
        pickle.dump(imbfs, fileout)
        fileout.close()

    return profile, nmbfs, nimbfs, mbfs_count, imbfs_count, t

def compute_all_nonadditive_imbfs(n, indir, outd = None):
    global count
    global outdir
    global variables
    global pset

    indir = indir + "/" if indir is not None else None
    outdir = outd + "/" if outd is not None else None

    variables = frozenset([(i + 1) for i in range(n)])
    pset = set([frozenset(p) for p in powerset(variables)])

    t1 = time.time()

    print("Number of CPUs: %d" % multiprocessing.cpu_count())

    pool = multiprocessing.Pool()
    n = 0
    for f in os.listdir(indir):
        if f.endswith(".pkl.bz2") is False:
            continue

        pool.apply_async(compute_nonadditive_mbfs,
                         (indir + f,),
                         callback = compute_nonadditive_mbfs_cb)

    pool.close()
    pool.join()

    print("total time: %.02f seconds" % (time.time() - t1))
    print("number of non-additive iMBFS: %d iMBFs" % total_imbfs_count)
    print("number of non-additive MBFS:  %d MBFs" % total_mbfs_count)

if __name__ == "__main__":
    import sys
    import multiprocessing

    if len(sys.argv) < 3:
        print("usage: %s n indir [outdir]" % sys.argv[0])
        sys.exit(1)

    outd = sys.argv[3] if len(sys.argv) > 3 else None
    compute_all_nonadditive_imbfs(int(sys.argv[1]), sys.argv[2], outd)
