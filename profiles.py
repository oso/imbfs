from __future__ import division
import math

def ncr(n, r):
    f = math.factorial
    return int(f(n) / f(r) / f(n - r))

def generate_profiles(n):
    K = {}
    for s in range(0, ncr(n, math.floor(n / 2)) + 1):
        K[0, s] = 0

    for r in range(1, n + 1):
        k = r
        K[r, 0] = 0
        for s in range(1, ncr(n, r) + 1):
            if s >= ncr(k, r):
                k = k + 1

            K[r, s] = K[r - 1, s - ncr(k - 1, r)] + ncr(k - 1, r - 1)

    P = set([tuple(0 for i in range(n))])
    for i in range(1, n + 1):
        P |= set([tuple([i] + [0 for i in range(n - 1)])])

    for r in range(2, n + 1):
        for s in range(1, ncr(n, r) + 1):
            Prs = set([p[:] for p in P if p[r - 2] >= K[r, s]])
            for p in Prs:
                p = list(p)
                p[r - 2] = p[r - 2] - K[r, s]
                p[r - 1] = s
                p = tuple(p)
                P |= set([p])

    return P

if __name__ == "__main__":
    profiles = generate_profiles(4)
    print(profiles)
    print(len(profiles))
