from __future__ import print_function
import bz2
import multiprocessing
import os
import pickle
import time
from utils import cpu_time
from utils import powerset
from kadditive import mbf_compute_mobius_and_lbda

nprofiles_done = 0
total_mbfs_count = 0
total_imbfs_count = 0
outdir_na = None
outdir_a = None
outdir_params = None
variables = None
kadditivity = 1
pset = None

def compute_nonkadditive_mbfs_cb(result):
    global total_mbfs_count
    global total_imbfs_count
    global nprofiles_done

    profile, nmbfs, nimbfs, na_mbfs_count, na_imbfs_count, t = result
    nprofiles_done += 1
    total_imbfs_count += na_imbfs_count
    total_mbfs_count += na_mbfs_count

    print("%d. Profile %s done!\t%10d (/%d) non-additives iMBFs (%d/%d MBFS) "
          "found (%.02f seconds)" % (nprofiles_done, str(profile),
          na_imbfs_count, nimbfs, na_mbfs_count, nmbfs, t))

def compute_nonkadditive_mbfs(filepath):
    global outdir_na
    global outdir_a
    global outdir_params
    global variables
    global pset
    global kadditivity

    t1 = cpu_time()

    f = bz2.BZ2File(filepath, 'rb')
    mbfs = pickle.load(f)

    na_mbfs_count = na_imbfs_count = 0
    a_mbfs_count = a_imbfs_count = 0
    na_imbfs, a_imbfs, a_imbfs_params = {}, {}, {}
    nmbfs = nimbfs = 0
    for mbf, n in mbfs.items():
        params = mbf_compute_mobius_and_lbda(mbf, kadditivity, variables,
                                             pset)
        if params is None:
            na_imbfs[mbf] = n
            na_imbfs_count += 1
            na_mbfs_count += n
        else:
            a_imbfs[mbf] = n
            a_imbfs_count += 1
            a_mbfs_count += n

            if outdir_params is not None:
                a_imbfs_params[mbf] = {'n': n, 'wmin': params[0],
                                       'wmax': params[2], 'lbdamin': params[1],
                                       'lbdamax': params[3]}

        nimbfs += 1
        nmbfs += n

    f.close()

    t = cpu_time() - t1

    profile = os.path.splitext(os.path.basename(filepath))[0]
    profile = os.path.splitext(profile)[0]
    profile = tuple(map(int, profile.split("-")))

    if outdir_na is not None and len(na_imbfs) > 0:
        filenameout = "-".join(map(str, profile)) + ".pkl.bz2"
        fileout = bz2.BZ2File(outdir_na + filenameout, 'wb')
        pickle.dump(na_imbfs, fileout)
        fileout.close()

    if outdir_a is not None and len(a_imbfs) > 0:
        filenameout = "-".join(map(str, profile)) + ".pkl.bz2"
        fileout = bz2.BZ2File(outdir_a + filenameout, 'wb')
        pickle.dump(a_imbfs, fileout)
        fileout.close()

    if outdir_params is not None and len(a_imbfs_params) > 0:
        filenameout = "-".join(map(str, profile)) + ".pkl.bz2"
        fileout = bz2.BZ2File(outdir_params + filenameout, 'wb')
        pickle.dump(a_imbfs_params, fileout)
        fileout.close()

    return profile, nmbfs, nimbfs, na_mbfs_count, na_imbfs_count, t

def compute_all_nonkadditive_imbfs(n, k, indir, outd_na = None, outd_a = None,
                                   outd_params = None):
    global count
    global outdir_na
    global outdir_a
    global outdir_params
    global variables
    global pset
    global kadditivity

    indir = indir + "/" if indir is not None else None
    outdir_na = outd_na + "/" if outd_na is not None else None
    outdir_a = outd_a + "/" if outd_a is not None else None
    outdir_params = outd_params + "/" if outd_params is not None else None

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

        pool.apply_async(compute_nonkadditive_mbfs,
                         (indir + f,),
                         callback = compute_nonkadditive_mbfs_cb)

    pool.close()
    pool.join()

    print("total time: %.02f seconds" % (time.time() - t1))
    print("number of non-additive iMBFS: %d iMBFs" % total_imbfs_count)
    print("number of non-additive MBFS:  %d MBFs" % total_mbfs_count)

if __name__ == "__main__":
    import sys
    from optparse import OptionParser

    usage = "%s n k indir [-n outdir_nadd] [-a outdir_add]\n" % sys.argv[0]
    usage += "with:\n"
    usage += "  n\t\t: number of variables\n"
    usage += "  k\t\t: k-additivity\n"
    usage += "  indir\t\t: directory in which IMBFs can be found"

    parser = OptionParser(usage = usage)
    parser.add_option("-n", "--nonadditive", dest="outd_na",
                      help="Directory in which non k-additive IMBFs are stored",
                      metavar="DIRECTORY")
    parser.add_option("-a", "--additive", dest="outd_a",
                      help="Directory in which k-additive IMBFs are stored",
                      metavar="DIRECTORY")
    parser.add_option("-s", "--store", dest="outd_params",
                      help="Directory in which k-additive IMBFs parameters are"
                           " stored",
                      metavar="DIRECTORY")
    (options, args) = parser.parse_args()

    if len(sys.argv) < 4:
        parser.print_help()
        sys.exit(1)

    outd_na = options.outd_na
    outd_a = options.outd_a
    outd_params = options.outd_params
    compute_all_nonkadditive_imbfs(int(sys.argv[1]), sys.argv[2], sys.argv[3],
                                   outd_na, outd_a, outd_params)
