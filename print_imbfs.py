from __future__ import print_function
import bz2
import os
import pickle
import sys
from utils import mbf_to_str

print_profile = False

def print_mbf_from_file(filepath):
    profile = os.path.basename(filepath)
    profile = os.path.splitext(os.path.splitext(profile)[0])[0]

    if print_profile is True:
        print("Profile: %s" % profile)

    f = bz2.BZ2File(filepath, 'rb')
    mbfs = pickle.load(f)
    f.close()

    for mbf, n in mbfs.items():
        print("I%s (%d MBFs)" % (mbf_to_str(mbf), n))

def main(argv):
    global print_profile

    argc = len(argv)
    if argc > 2:
        print_profile = True

    for i, f in enumerate(argv[1:]):
        print_mbf_from_file(f)
        if i < (argc - 2):
            print("")

if __name__ == "__main__":
    main(sys.argv)
