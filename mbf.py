from __future__ import print_function
from copy import deepcopy
from itertools import combinations, product
from profiles import generate_profiles
import resource

class coa(frozenset):

    def __repr__(self):
        return "coa(%s)" % ', '.join(map(str, self))

class coaset(frozenset):

    def __repr__(self):
        return "coaset(%s)" % ', '.join(map(str, self))

def cpu_time():
    return resource.getrusage(resource.RUSAGE_SELF)[0]

def compute_all_coalitions(variables, profiles):
    combis = {}
    for i in range(len(variables)):
        coalitions = set(coa(c) for c in combinations(variables, i + 1))

        kmax = max([profile[i] for profile in profiles])
        for k in range(1, kmax + 1):
            combis[i, k] = set()
            for c in combinations(coalitions, k):
                combis[i, k].add(coaset(c))

    return combis

def drop_supersets(combis, coalitionsset):
    for coa in coalitionsset:
        for combi in combis:
            for cset in combi.copy():
                for coa2 in cset:
                    if coa2 > coa:
                        combi.discard(cset)

def compute_mbf(mbfs, combis, mbf):
    if len(combis) == 0:
        return

    for combi in combis.pop(0):
        mbf_new = mbf.copy()
        mbf_new |= combi

        if len(combis) == 0:
            mbfs.add(frozenset(mbf_new))
        else:
            combis_new = deepcopy(combis)
            drop_supersets(combis_new, combi)
            compute_mbf(mbfs, combis_new, mbf_new)

def mbf_from_profiles(variables, profile, coalitions):
    n = len(variables)

    l = []
    for i, k in enumerate(profile):
        if k < 1:
            continue

        l.append(coalitions[i, k])

    mbfs = set()
    compute_mbf(mbfs, l[:], coaset())

    return mbfs

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("usage: %s n" % sys.argv[0])
        sys.exit(1)

    n = sys.argv[1]
    variables = tuple(["c%d" % (i + 1) for i in range(int(n))])
    print(variables)
    profiles = generate_profiles(len(variables))
    combis = compute_all_coalitions(variables, profiles)

    n = 0
    for i, profile in enumerate(profiles):
        print("%d. Processing profile %s..." % ((i + 1), str(profile)),
              end = "")
        t1 = cpu_time()
        k = len(mbf_from_profiles(variables, profile, combis))
        print("\t%10d MBFs found (%.02f seconds)" % (k, (cpu_time() - t1)));
        n += k

    print(n)
