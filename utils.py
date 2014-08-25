import resource
from itertools import chain, combinations

def cpu_time():
    return sum(resource.getrusage(resource.RUSAGE_SELF)[:2])

def mbf_to_str(mbf):
    string = "MBF("
    if len(mbf) == 0:
        return string + ")"

    for s in mbf:
        string += "[" + ", ".join(map(str, s)) + "], "
    string = string[:-2] + ")"
    return string

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))
