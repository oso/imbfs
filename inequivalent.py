import itertools

def compute_permutations(variables):
    return [dict(zip(variables, i))
            for i in itertools.permutations(variables, len(variables))][1:]

def permute_indices(mbf, perm):
    f = lambda i: perm[i]

    mbfeq = set()
    for coa in mbf:
        coaeq = frozenset(map(f, coa))
        mbfeq.add(coaeq)

    return mbfeq

def find_inequivalent_mbfs(mbfs, perms):
    imbfs = dict()

    while len(mbfs) > 0:
        mbf = mbfs.pop()
        imbfs[mbf] = 1

        for perm in perms:
            mbfeq = permute_indices(mbf, perm)
            for mbf2 in mbfs.copy():
                if mbfeq == mbf2:
                    mbfs.discard(mbf2)
                    imbfs[mbf] += 1

    return imbfs

if __name__ == "__main__":
    import sys
    from mbf import compute_all_coalitions
    from mbf import mbfs_from_profiles

    variables = (1, 2, 3, 4)
    profile = (0, 3, 0, 0)

    combis = compute_all_coalitions(variables, [profile])
    mbfs = mbfs_from_profiles(variables, profile, combis)

    perms = compute_permutations(variables)
    print(perms)

    imbfs = find_inequivalent_mbfs(mbfs, perms)
    print(imbfs)
