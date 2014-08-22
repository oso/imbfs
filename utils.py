import resource

def cpu_time():
    return sum(resource.getrusage(resource.RUSAGE_SELF)[:2])
