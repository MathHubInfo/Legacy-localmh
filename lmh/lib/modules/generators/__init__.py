from multiprocessing import current_process
from multiprocessing.pool import Pool
import atexit
import traceback
import re
import time
import os.path

try:
    import signal
except:
    pass

from lmh.lib.io import std, err, term_colors, write_file

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

    if text != None:
        try:
            text_ = text
            text = re.compile(text)
            std("Compiling regular expression: ", newline=False)
            std(text_)
        except:
            err("Invalid regular expression. ")
            return (False, [], [])


    # All the modules which need to be generated should be added in the list
    for m in modules:
        if the_generator.needs_file(m, update_mode, text=text):
            jobs.append((m, the_generator.make_job(m)))

    if len(jobs) == 0:
        if simulate:
            std("#"+the_generator.prefix+":", "No jobs, nothing to do. ")
        else:
            std(the_generator.prefix+":", "No jobs, nothing to do. ")
        return (True, [], [])

    # If we have fewer jobs than workers, scale down the number of workers
    # We assume the number of jobs is non-empty, as above.
    if len(jobs) < num_workers:
        if not quiet:
            std(the_generator.prefix+":", "Less jobs then available workers, using fewer workers. ")
        num_workers = len(jobs)

    if simulate:
        return run_simulate(the_generator, jobs, quiet)
    else:
        try:
            (r, d, f) = run_generate(the_generator, num_workers, jobs, quiet)
        except Exception as e:
            write_log_files(the_generator, d, f)
            raise e
        write_log_files(the_generator, d, f)
        return (r, d, f)

class WorkRunnerJob(object):
    def __init__(self, quiet, the_generator):
        self.quiet = quiet
        self.the_generator = the_generator
    def __call__(self, j):
        try:
            return worker_runner(j, self.quiet, self.the_generator)
        except KeyboardInterrupt:
            err(self.the_generator.prefix+":", "Generation aborted, use CTRL-Z to terminate pool. ")
        except Exception as e:
            err("Exception in Worker Process: ")
            err(traceback.format_exc())
        return False

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

        std(the_generator.prefix+":", len(jobs), "file(s) to generate using", num_workers,"workers. ")

        # Create the worker Pool
        the_worker_pool = Pool(num_workers, worker_initer, [the_generator])

        res = the_worker_pool.map(WorkRunnerJob(quiet, the_generator), jobs)

        try:
            def kill_handler():
                err(the_generator.prefix+":", "Received SIGTERM, aborting. ")
                the_worker_pool.terminate()
            signal.signal(kill_handler, signal.SIGTERM)
        except:
            pass

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
        std(the_generator.prefix+":", len(jobs), "file(s) to generate using 1 worker. ")

        for (m, j) in jobs:
            if not run_generate_single(the_generator, None, (m, j), quiet):
                if not quiet:
                    err(the_generator.prefix+":", "Did not generate", term_colors("red")+the_generator.get_log_name(m)+term_colors("normal"), colors=False)
                fails.append(m)
            else:
                if not quiet:
                    std(the_generator.prefix+":", "Generated", term_colors("green")+the_generator.get_log_name(m)+term_colors("normal"))
                successes.append(m)

        if not the_generator.run_deinit(None):
            err("Unable to deintialise main Worker. ")
            return (False, successes, fails)
    return (True, successes, fails)

def get_wid():
    return current_process()._identity[0]

def worker_initer(the_generator):
    worker_id = get_wid()

    def worker_deiniter():
        if not the_generator.run_deinit(worker_id):
            err("Unable to deinitalise worker", worker_id)
            raise "UnableToDeInit"

    atexit.register(lambda: worker_deiniter)

    if not the_generator.run_init(worker_id):
        err("Unable to initalise worker", worker_id)
        raise "UnableToInit"

def worker_runner(job, quiet, the_generator):
    worker_id = get_wid()
    prefix = the_generator.prefix+"["+str(worker_id)+"]:"
    (m, j) = job

    if not run_generate_single(the_generator, worker_id, (m, j), quiet):
        if not quiet:
            err(prefix, "Did not generate", term_colors("red")+the_generator.get_log_name(m)+term_colors("normal"), colors=False)
        return False
    else:
        if not quiet:
            std(prefix, "Generated", term_colors("green")+the_generator.get_log_name(m)+term_colors("normal"))
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

def write_log_files(the_generator, ds, fs):

    logs = {}

    for d in ds:
        try:
            if d["path"] in logs:
                logs[d["path"]]["dones"].append(os.path.relpath(the_generator.get_log_name(d), d["path"]))
            else:
                logs[d["path"]] = {"dones": [os.path.relpath(the_generator.get_log_name(d), d["path"])], "fails": []}
        except:
            pass
    for f in fs:
        if f["path"] in logs:
            logs[f["path"]]["fails"].append(os.path.relpath(the_generator.get_log_name(f), f["path"]))
        else:
            logs[f["path"]] = {"dones": [], "fails": [os.path.relpath(the_generator.get_log_name(f), f["path"])]}

    # The file name to add
    fname = "."+the_generator.prefix.lower()+".log"

    for l in logs:
        write_file(os.path.join(l, fname), "lmh "+the_generator.prefix.lower()+" log file, generated "+time.strftime("%Y-%m-%d-%H-%M-%S")+"\nGenerated: \n"+"\n".join(logs[l]["dones"])+"\nDid not generate: \n\n"+"\n".join(logs[l]["fails"]))





# Import all the generators.
# This has to be at the end of the file
from lmh.lib.modules.generators.sms import generate as sms
from lmh.lib.modules.generators.localpaths import generate as localpaths
from lmh.lib.modules.generators.alltex import generate as alltex
from lmh.lib.modules.generators.omdoc import generate as omdoc
from lmh.lib.modules.generators.pdf import generate as pdf
from lmh.lib.modules.generators.xhtml import generate as xhtml
