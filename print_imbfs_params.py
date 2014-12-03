from __future__ import print_function
import bz2
import os
import pickle
import sys
from utils import mbf_to_str

print_profile = False

def print_mobius_lbda(m, lbda):
    mnames = {"[%s]" % (', '.join(str(i) for i in sorted(c))): c
              for c in m.keys() }
    for mname in sorted(mnames.keys(), key = lambda x: "%d-%s" % (len(x), x)):
        fset = mnames[mname]
        print("%s: %f" % (mname, m[fset]), end = ', ')

    print("lambda: %f" % lbda)

def print_mbf_from_file(filepath):
    profile = os.path.basename(filepath)
    profile = os.path.splitext(os.path.splitext(profile)[0])[0]

    if print_profile is True:
        print("Profile: %s" % profile)

    f = bz2.BZ2File(filepath, 'rb')
    mbfs = pickle.load(f)
    f.close()

    nmbfs = nimbfs = 0
    for mbf, d in mbfs.items():
        print("I%s (%d MBFs)" % (mbf_to_str(mbf), d['n']))
        print('  LAMBDA min: ', end = '')
        print_mobius_lbda(d['wmin'], d['lbdamin'])
        print('  LAMBDA max: ', end = '')
        print_mobius_lbda(d['wmax'], d['lbdamax'])
        nmbfs += d['n']
        nimbfs += 1

    return nimbfs, nmbfs

def main(argv):
    global print_profile

    argc = len(argv)
    if argc > 2:
        print_profile = True

    total_mbfs = total_imbfs = 0
    for f in argv[1:]:
        if f.endswith(".pkl.bz2") is False:
            continue

        nimbfs, nmbfs = print_mbf_from_file(f)
        print("")
        total_imbfs += nimbfs
        total_mbfs += nmbfs

    print("Total IMBFs: %d IMBFs" % total_imbfs)
    print("Total MBFs : %d MBFs" % total_mbfs)

if __name__ == "__main__":
    main(sys.argv)
