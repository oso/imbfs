from __future__ import print_function
import multiprocessing
from profiles import generate_profiles
from mbf import compute_all_coalitions
from mbf import mbf_from_profiles
from mbf import cpu_time


count = 0

def compute_number_of_mbfs_cb(result):
    global count

    profile, k, t = result
    print("Profile %s done!\t%10d MBFs found (%.02f seconds)"
          % (str(profile), k, t));
    count += k

def compute_number_of_mbfs(variables, profile, combis):
    t1 = cpu_time()

    try:
        k = len(mbf_from_profiles(variables, profile, combis))
    except:
        import traceback
        print("Error with profile %s" % str(profile))
        print(traceback.format_exc())

    t = cpu_time() - t1

    return profile, k, t

def compute_all_mbfs(n):
    global count

    print("Number of variables: %d" % n)
    print("Number of CPUs: %d" % multiprocessing.cpu_count())

    variables = tuple(["c%d" % (i + 1) for i in range(int(n))])

    profiles = generate_profiles(len(variables))
    combis = compute_all_coalitions(variables, profiles)

    pool = multiprocessing.Pool()
    n = 0
    for i, profile in enumerate(profiles):
        pool.apply_async(compute_number_of_mbfs,
                         (variables, profile, combis),
                         callback = compute_number_of_mbfs_cb)

    pool.close()
    pool.join()

    print("total time: %.02f seconds" % cpu_time())
    print(count)

if __name__ == "__main__":
    import sys
    import multiprocessing

    if len(sys.argv) != 2:
        print("usage: %s n" % sys.argv[0])
        sys.exit(1)

    compute_all_mbfs(int(sys.argv[1]))
