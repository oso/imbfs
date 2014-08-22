from __future__ import print_function
import multiprocessing
import os
import pickle
import time
from utils import cpu_time
from inequivalent import compute_permutations
from inequivalent import find_inequivalent_mbfs

nprofiles_done = 0
count = 0
permutations = None
outdir = None

def compute_number_of_inequivalent_mbfs_cb(result):
    global count
    global nprofiles_done

    profile, nmbfs, nimbfs, t = result
    nprofiles_done += 1
    count += nimbfs

    print("%d. Profile %s done!\t%10d (/%d) inequivalent MBFs found " \
          "(%.02f seconds)" % (nprofiles_done, str(profile), nimbfs, nmbfs, t))

def compute_inequivalent_mbfs(filepath):
    global permutations
    global outdir

    t1 = cpu_time()

    f = open(filepath)
    mbfs = pickle.load(f)
    nmbfs = len(mbfs)
    imbfs = find_inequivalent_mbfs(mbfs, permutations)
    f.close()

    t = cpu_time() - t1

    profile = os.path.splitext(os.path.basename(filepath))[0]
    profile = tuple(map(int, profile.split("-")))

    if outdir is not None:
        filenameout = "-".join(map(str, profile)) + ".pkl"
        fileout = open(outdir + filenameout, 'wb')
        pickle.dump(imbfs, fileout)
        fileout.close()

    return profile, nmbfs, len(imbfs), t

def compute_all_inequivalent_mbfs(n, indir, outd = None):
    global count
    global outdir
    global permutations

    indir = indir + "/" if indir is not None else None
    outdir = outd + "/" if outd is not None else None

    n = tuple((i + 1) for i in range(n))
    permutations = compute_permutations(n)

    t1 = time.time()

    print("Number of CPUs: %d" % multiprocessing.cpu_count())

    pool = multiprocessing.Pool()
    n = 0
    for f in os.listdir(indir):
        if f.endswith(".pkl") is False:
            continue

        pool.apply_async(compute_inequivalent_mbfs,
                         (indir + f,),
                         callback = compute_number_of_inequivalent_mbfs_cb)

    pool.close()
    pool.join()

    print("total time: %.02f seconds" % (time.time() - t1))
    print(count)

if __name__ == "__main__":
    import sys
    import multiprocessing

    if len(sys.argv) < 3:
        print("usage: %s n indir [outdir]" % sys.argv[0])
        sys.exit(1)

    outd = sys.argv[3] if len(sys.argv) > 3 else None
    compute_all_inequivalent_mbfs(int(sys.argv[1]), sys.argv[2], outd)
