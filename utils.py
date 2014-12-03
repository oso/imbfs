import resource
from itertools import chain, combinations

def cpu_time():
    return sum(resource.getrusage(resource.RUSAGE_SELF)[:2])

def mbf_to_str(mbf):
    string = "MBF("
    if mbf is None:
        return strin + ")"
    elif len(mbf) == 0:
        return string + "[])"

    sortfn = lambda x: "%d-%s" % (len(x), "".join(str(sorted(x))))
    for s in sorted(mbf, key = sortfn):
        string += "[" + ", ".join(map(str, s)) + "], "
    string = string[:-2] + ")"
    return string

def mbf_str_hash(mbf):
    sortfn = lambda x: "%d-%s" % (len(x), "".join(str(sorted(x))))
    return "-".join(map(str, ["".join(map(str, s))
                              for s in sorted(mbf, key = sortfn)]))

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))
