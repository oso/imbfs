from __future__ import print_function
import multiprocessing
import pickle
from profiles import generate_profiles
from mbf import compute_all_coalitions
from mbf import mbf_from_profiles
from mbf import cpu_time

nprofiles_done = 0
count = 0
savedir = None

def compute_number_of_mbfs_cb(result):
    global count
    global nprofiles_done

    profile, k, t = result
    nprofiles_done += 1
    count += k

    print("%d. Profile %s done!\t%10d MBFs found (%.02f seconds)"
          % (nprofiles_done, str(profile), k, t));

def compute_number_of_mbfs(variables, profile, combis):
    global savedir

    t1 = cpu_time()

    try:
        mbfs = mbf_from_profiles(variables, profile, combis)
    except:
        import traceback
        print("Error with profile %s" % str(profile))
        print(traceback.format_exc())

    t = cpu_time() - t1

    if savedir is not None:
        filenameout = "-".join(map(str, profile)) + ".pkl"
        fileout = open(savedir + filenameout, 'wb')
        pickle.dump(mbfs, fileout)
        fileout.close()

    return profile, len(mbfs), t

def compute_all_mbfs(n):
    global count

    print("Number of variables: %d" % n)
    print("Number of CPUs: %d" % multiprocessing.cpu_count())

    variables = tuple([(i + 1) for i in range(int(n))])

    profiles = generate_profiles(len(variables))
    print("Number of profiles: %d" % len(profiles))

    combis = compute_all_coalitions(variables, profiles)

    pool = multiprocessing.Pool()
    n = 0
    for profile in profiles:
        combi = {(i, n): combis[i, n] for i, n in enumerate(profile) if n > 0}

        pool.apply_async(compute_number_of_mbfs,
                         (variables, profile, combi),
                         callback = compute_number_of_mbfs_cb)

    pool.close()
    pool.join()

    print("total time: %.02f seconds" % cpu_time())
    print(count)

if __name__ == "__main__":
    import sys
    import multiprocessing

    if len(sys.argv) < 2:
        print("usage: %s n [savedir]" % sys.argv[0])
        sys.exit(1)

    savedir = sys.argv[2] + "/" if len(sys.argv) > 2 else None
    compute_all_mbfs(int(sys.argv[1]))
