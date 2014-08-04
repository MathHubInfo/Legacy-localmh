from multiprocessing import current_process
from multiprocessing.pool import Pool
import atexit

from lmh.lib.io import std, err

class Generator():
    def __init__(self, quiet, **config):
        # Inits options
        self.supportsMoreThanOneWorker = True # Do we allow more than one worker?
        self.prefix = "GEN" # Some prefix for logs
    def needs_file(self,module, gen_mode, text=None):
        # Check if we need a job
        return False
    def make_job(self,module):
        # Creates a job from a file
        pass
    def run_init(self,worker_id):
        # Initlaises Running jobs (called once per worker, worker_id == None => Master)
        return True
    def run_deinit(self, worker_id):
        # Deinitalises running jobs (called once per worker, worker_id == None => Master)
        return True
    def run_job(self,job,worker_id):
        # Runs a single job
        return True
    def dump_init(self):
        # initialisation code for dumping.
        return True
    def dump_deinit(self):
        # deinitalisation code for dumping.
        return True
    def dump_job(self, job):
        # Dumps a job to the command line.
        return True
    def get_log_name(self, module):
        return module["file"]

def run(modules, simulate, update_mode, quiet, num_workers, GeneratorClass, text, **config):

    # Create generator and job list
    the_generator = GeneratorClass(quiet, **config)
    jobs = []

    # All the modules which need to be generated should be added in the list
    for m in modules:
        if the_generator.needs_file(m, update_mode, text=text):
            jobs.append((m, the_generator.make_job(m)))

    if simulate:
        return run_simulate(the_generator, jobs, quiet)
    else:
        return run_generate(the_generator, num_workers, jobs, quiet)

class WorkRunnerJob(object):
    def __init__(self, quiet, the_generator):
        self.quiet = quiet
        self.the_generator = the_generator
    def __call__(self, j):
        return worker_runner(j, self.quiet, self.the_generator)

def run_simulate(the_generator, jobs, quiet):

    # Initialise dumping or fail
    if not the_generator.dump_init():
        if not quiet:
            err("Unable to initalise with --simulate. ")
        return (False, [], [])

    # Run all of the jobs
    for (m, j) in jobs:
        if not the_generator.dump_job(j):
            if not quiet:
                err("Unable to dump job. ")
            return (False, [], [])

    # Deinitalise everything
    if not the_generator.dump_deinit():
        err("Unable to deinitalise with --simulate. ")
        return (False, [], [])

    # Thats it
    return (True, [], [])

def run_generate(the_generator, num_workers, jobs, quiet):
    # What worked, what didn't
    successes = []
    fails = []

    if the_generator.supportsMoreThanOneWorker and num_workers != 1:
        # Multiple Code here
        if not the_generator.run_init(None):
            err("Unable to intialise main Worker. ")
            return False

        # Create the worker Pool
        the_worker_pool = Pool(num_workers, worker_initer, [the_generator])

        res = the_worker_pool.map(WorkRunnerJob(quiet, the_generator), jobs)

        the_worker_pool.close()
        the_worker_pool.join()

        for (r, (m, j)) in zip(res, jobs):
            if r:
                successes.append(m)
            else:
                fails.append(m)
    else:
        if not the_generator.run_init(None):
            err("Unable to intialise main Worker. ")
            return (False, successes, fails)

        # Run all of the jobs
        for (m, j) in jobs:
            if not run_generate_single(the_generator, None, (m, j), quiet):
                if not quiet:
                    err(the_generator.prefix, "Did not generate", the_generator.get_log_name(m))
                    return (False, successes, fails)
                fails.append(m)
            else:
                if not quiet:
                    std(the_generator.prefix, "Generated", the_generator.get_log_name(m))
                successes.append(m)

        if not the_generator.run_deinit(None):
            err("Unable to deintialise main Worker. ")
            return (False, successes, fails)
    return (True, successes, fails)

def worker_initer(the_generator):
    worker_id = current_process()._identity[0]

    def worker_deiniter():
        if not the_generator.run_deinit(worker_id):
            err("Unable to deinitalise worker", worker_id)
            raise "UnableToDeInit"

    atexit.register(lambda: worker_deiniter)

    if not the_generator.run_init(worker_id):
        err("Unable to initalise worker", worker_id)
        raise "UnableToInit"

def worker_runner(job, quiet, the_generator):
    worker_id = current_process()._identity[0]
    prefix = the_generator.prefix+"["+str(worker_id)+"]:"
    (m, j) = job

    if not run_generate_single(the_generator, worker_id, (m, j), quiet):
        if not quiet:
            err(prefix, "Did not generate", the_generator.get_log_name(m))
            return (False, successes, fails)
        return False
    else:
        if not quiet:
            std(prefix, "Generated", the_generator.get_log_name(m))
        return True


def run_generate_single(the_generator, worker_id, job, quiet):
    (m, j) = job

    #Print out a debug message
    if not quiet:
        if worker_id == None:
            std(the_generator.prefix+": Generating", the_generator.get_log_name(m))
        else:
            std(the_generator.prefix+"["+str(worker_id)+"]: Generating", the_generator.get_log_name(m))

    # Run a job
    return the_generator.run_job(j, worker_id)


# Import all the generators.
# This has to be at the end of the file
from lmh.lib.modules.generators.sms import generate as sms
from lmh.lib.modules.generators.localpaths import generate as localpaths
from lmh.lib.modules.generators.alltex import generate as alltex
