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

def cplex_lbda_minmax(variables, fmins, gmaxs, kadditivity, epsilon = 0.0001):
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
    lp.variables.add(names = ["gammaf_%d" % i for i in range(len(fmins))],
                              types = [lp.variables.type.binary
                                       for i in range(len(fmins))])
    lp.variables.add(names = ["gammag_%d" % i for i in range(len(gmaxs))],
                              types = [lp.variables.type.binary
                                       for i in range(len(gmaxs))])

    lp.linear_constraints.add(names = ["fmin%s" % i
                                       for i in range(len(fmins))],
                              lin_expr =
                                [
                                 [wlist + ["lambda"] + ["gammaf_%d" % i],
                                  [1 if w in fmobius[fmin] else 0 for w in wlist]
                                  + [-1] + [1]
                                 ] for i, fmin in enumerate(fmins)
                                ],
                              senses = ["G" for fmin in fmins],
                              rhs = [0 for fmin in fmins])

    lp.linear_constraints.add(names = ["gmax%s" % i
                                       for i in range(len(gmaxs))],
                              lin_expr =
                                [
                                 [wlist + ["lambda"] + ["gammag_%d" % i],
                                  [1 if w in gmobius[gmax] else 0 for w in wlist]
                                  + [-1] + [-1]
                                 ] for i, gmax in enumerate(gmaxs)
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

    lp.objective.set_linear([("gammaf_%d" % i, 1)
                             for i in range(len(fmins))] +
                            [("gammag_%d" % i, 1)
                             for i in range(len(gmaxs))])
    lp.objective.set_sense(lp.objective.sense.minimize)

    lp.solve()
    status = lp.solution.get_status()
    if status != lp.solution.status.MIP_optimal:
        return None

    n = lp.solution.get_objective_value()

    return n

def generate_binary_table(pset, fmins):
    good = set([])
    bad = set([])
    for coalition in pset:
        is_good = False
        for fmin in fmins:
            if coalition >= fmin:
                is_good = True

        if is_good is True:
            good.add(coalition)
        else:
            bad.add(coalition)

    return frozenset(good), frozenset(bad)

def mbf_ca_kadditive(mbf, kadditivity, variables, pset):
    good, bad = generate_binary_table(pset, mbf)
    n = cplex_lbda_minmax(variables, good, bad, kadditivity)
    return n

if __name__ == "__main__":
    from utils import mbf_to_str

    kadditivity = 1
    n = 4
    variables = frozenset([(i + 1) for i in range(n)])
    pset = set([frozenset(p) for p in powerset(variables)])
    mbf = frozenset([frozenset([1, 2]), frozenset([1, 4]), frozenset([3, 4])])

    n = mbf_ca_kadditive(mbf, kadditivity, variables, pset)
    print("%s: %d/%d are not representable with %d-additive weights"
          % (mbf_to_str(mbf), n, len(pset), kadditivity))
