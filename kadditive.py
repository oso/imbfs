import bz2
import cplex
import math
import sys
from itertools import combinations
from itertools import product
from utils import powerset

def get_mobius_indices_from_mbf(fmins, kadditivity):
    mobius = {}
    for fmin in fmins:
        mobius[fmin] = set()
        for k in range(1, kadditivity + 1):
            mobius[fmin] |= set([str(frozenset(c))
                                 for c in combinations(fmin, k)])

    return mobius

def cplex_lbda_minmax(variables, fmins, gmaxs, kadditivity, epsilon = 0.00001):
    lp = cplex.Cplex()
    lp.set_log_stream(None)
    lp.set_results_stream(None)

    wks = {}
    variables = set(variables)
    for k in range(1, kadditivity + 1):
        wks[k] = set([frozenset(c) for c in combinations(variables, k)])

    wlist = list()
    for val in wks.values():
        wlist += list(val)
    wlist = map(str, wlist)

    fmobius = get_mobius_indices_from_mbf(fmins, kadditivity)
    gmobius = get_mobius_indices_from_mbf(gmaxs, kadditivity)

    lp.variables.add(names = wlist, lb = [-1 for w in wlist],
                                    ub = [1 for w in wlist])
    lp.variables.add(names = ["lambda"], lb = [0], ub = [1 + epsilon])

    lp.linear_constraints.add(names = ["fmin%s" % i
                                       for i in range(len(fmins))],
                              lin_expr =
                                [
                                 [wlist + ["lambda"],
                                  [1 if w in fmobius[fmin] else 0 for w in wlist]
                                  + [-1]
                                 ] for fmin in fmins
                                ],
                              senses = ["G" for fmin in fmins],
                              rhs = [0 for fmin in fmins])

    lp.linear_constraints.add(names = ["gmax%s" % i
                                       for i in range(len(gmaxs))],
                              lin_expr =
                                [
                                 [wlist + ["lambda"],
                                  [1 if w in gmobius[gmax] else 0 for w in wlist]
                                  + [-1]
                                 ] for gmax in gmaxs
                                ],
                              senses = ["L" for gmax in gmaxs],
                              rhs = [-epsilon for gmax in gmaxs])

    lp.linear_constraints.add(names = ["wsum"],
                              lin_expr = [
                                          [wlist, [1.0] * len(wlist)],
                                          ],
                              senses = ["E"],
                              rhs = [1]
                             )

    for variable in variables:
        _variables = variables ^ set([variable])
        ml = [frozenset([variable])]
        for k in range(1, kadditivity):
            ml += [frozenset(set(c) | set([variable]))
                   for c in combinations(_variables, k)]
        ml = map(str, ml)

        coef = [[1 if i <= j else 0 for i in range(len(ml))]
                for j in range(len(ml))]
        coef = list(product([0, 1], repeat = len(ml) - 1))
        coef = map(list, coef)

        lp.linear_constraints.add(names = ["m_%s_%d" % (str(variable), i)
                                           for i in range(len(coef))],
                                  lin_expr = [
                                              [ml,
                                               [1] + coef[i]
                                              ] for i in range(len(coef))
                                             ],
                                  senses = ["G" for i in coef],
                                  rhs = [0 for i in coef]
                                 )

    lp.objective.set_linear("lambda", 1)

    lp.objective.set_sense(lp.objective.sense.minimize)
    lp.solve()
    status = lp.solution.get_status()
    if status != lp.solution.status.optimal:
        return None

    wmin = dict(zip(wlist, lp.solution.get_values(wlist)))
    lbdamin = lp.solution.get_objective_value()

    lp.objective.set_sense(lp.objective.sense.maximize)
    lp.solve()

    wmax = dict(zip(wlist, lp.solution.get_values(wlist)))
    lbdamax = lp.solution.get_objective_value()

    return wmin, lbdamin, wmax, lbdamax

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

def mbf_is_kadditive(mbf, kadditivity, variables, pset):
    gmaxs = compute_gmax(pset, mbf)
    additive = cplex_lbda_minmax(variables, mbf, gmaxs, kadditivity)
    return False if additive is None else True

def mbf_compute_mobius_and_lbda(mbf, kadditivity, variables, pset):
    gmaxs = compute_gmax(pset, mbf)
    return cplex_lbda_minmax(variables, mbf, gmaxs, kadditivity)

if __name__ == "__main__":
    from utils import mbf_to_str

    kadditivity = 2
    n = 4
    variables = frozenset([(i + 1) for i in range(n)])
    pset = set([frozenset(p) for p in powerset(variables)])
    mbf = frozenset([frozenset([1, 2]), frozenset([1, 4]), frozenset([3, 4])])

    additive = mbf_is_kadditive(mbf, kadditivity, variables, pset)
    print("%s is %s%sadditive" % (mbf_to_str(mbf),
                                "" if additive is True else "NOT ",
                                "%d-" % kadditivity))
