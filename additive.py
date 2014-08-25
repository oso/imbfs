import bz2
import cplex
import math
import sys
from itertools import product
from utils import powerset

def cplex_lbda_minmax(cids, fmins, gmaxs, epsilon = 0.00001):
    lp = cplex.Cplex()
    lp.set_log_stream(None)
    lp.set_results_stream(None)

    lp.variables.add(names = ["w%s" % cid for cid in cids],
                     lb = [0 for c in cids],
                     ub = [1 for c in cids])
    lp.variables.add(names = ["lambda"], lb = [0], ub = [1 + epsilon])

    lp.linear_constraints.add(names = ["fmin%s" % i
                                       for i in range(len(fmins))],
                              lin_expr =
                                [
                                 [["w%s" % cid for cid in cids] + ["lambda"],
                                  [1 if cid in fmin else 0 for cid in cids]
                                  + [-1]
                                 ] for fmin in fmins
                                ],
                              senses = ["G" for fmin in fmins],
                              rhs = [0 for fmin in fmins])

    lp.linear_constraints.add(names = ["gmax%s" % i
                                       for i in range(len(gmaxs))],
                              lin_expr =
                                [
                                 [["w%s" % cid for cid in cids] + ["lambda"],
                                  [1 if cid in gmax else 0 for cid in cids]
                                  + [-1]
                                 ] for gmax in gmaxs
                                ],
                              senses = ["L" for gmax in gmaxs],
                              rhs = [-epsilon for gmax in gmaxs])

    lp.linear_constraints.add(names = ["wsum"],
                              lin_expr = [
                                          [["w%s" % cid for cid in cids],
                                           [1.0] * len(cids)],
                                         ],
                              senses = ["E"],
                              rhs = [1]
                             )

    lp.objective.set_linear("lambda", 1)

    lp.objective.set_sense(lp.objective.sense.minimize)
    lp.solve()
    status = lp.solution.get_status()
    if status != lp.solution.status.optimal:
        return None

    lbdamin = lp.solution.get_objective_value()

    lp.objective.set_sense(lp.objective.sense.maximize)
    lp.solve()
    lbdamax = lp.solution.get_objective_value()

    return lbdamin, lbdamax

def compute_gmax(pset, fmins):
    gmaxs = pset.copy()
    for s, fmin in product(gmaxs, fmins):
        if fmin.issubset(s):
            gmaxs.discard(s)

    for s, s2 in product(gmaxs, gmaxs):
        if s == s2:
            continue
        elif s2.issubset(s):
            gmaxs.discard(s2)

    return gmaxs

def mbf_is_additive(mbf, variables, pset):
    gmaxs = compute_gmax(pset, mbf)
    lbdas = cplex_lbda_minmax(variables, mbf, gmaxs)
    return False if lbdas is None else True

if __name__ == "__main__":
    from utils import mbf_to_str

    n = 4
    variables = frozenset([(i + 1) for i in range(n)])
    pset = set([frozenset(p) for p in powerset(variables)])
    mbf = frozenset([frozenset([1, 2]), frozenset([1, 4]), frozenset([3, 4])])

    additive = mbf_is_additive(mbf, variables, pset)
    print("%s is %sadditive" % (mbf_to_str(mbf),
                                "" if additive is True else "NOT "))
