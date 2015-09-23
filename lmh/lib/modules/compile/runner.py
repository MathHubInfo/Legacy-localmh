from lmh.lib.modules import get_build_groups
from lmh.lib.io import std, err
from multiprocessing import Pool, current_process, TimeoutError
from lmh.lib.modules.compile.scripter import make_build_script
from lmh.lib.repos.local.dirs import find_repo_dir
from lmh.lib.mmt import run_script

import os
import traceback

def get_unique_process_id():
    try:
        return current_process()._identity[0]
    except:
        return 0

def run_compilation_process(workload):
    try:

        # get identity of current process and work to do.
        worker_num = get_unique_process_id()

        (rgroup, args) = workload
        (repo, files) = rgroup
        (targets, quiet) = args

        # give some nice debugging output
        std("Worker["+str(worker_num)+"]:", "Generating content for", repo)
        std("Worker["+str(worker_num)+"]:", len(files), "item to generate content for. ")

        # generate the script and run it.
        script = make_build_script(rgroup, targets, quiet, worker_num)
        ret = run_script(script, path=find_repo_dir(repo))

        # More logging
        std("Worker["+str(worker_num)+"]: Finished working on "+repo)

        # thats it.
        return ret

    # for keyboard interrupts, do not print
    except KeyboardInterrupt as e:
        return False
    except Exception as e:
        print(e)
        err(traceback.format_exc(e))
        return False

def build_targets(args):

    targets = {"list": False}

    if args.sms:
        targets["sms"] = {}
    if args.omdoc:
        targets["omdoc"] = {}
    if args.pdf:
        targets["pdf"] = {}
    if args.list:
        targets["list"] = True

    return targets

def run_paralell(spec, num_workers, targets, quiet):
    # resolve groups and count.
    std("Resolving for content to be generated, this might take a bit ...")
    groups = get_build_groups(spec)
    num = sum([len(f) for (r, f) in groups])

    std("Done, found", len(groups), "repositories to generate a total of", num, "items. ")

    if len(groups) == 0:
        std("Nothing to do, exiting ...")
        return True

    # if we have more workers, use fewer.
    if num_workers > len(groups):
        std("More workers than repositories, using fewer workers. ")
        num_workers = len(groups)

    # Build arguments
    args = (targets, quiet)

    # Make a pool.
    p = Pool(num_workers)

    # and run it and prepare to get the exception

    runner = p.map_async(run_compilation_process, (map(lambda x:(x, args), groups)))
    while True:
        try:
            return runner.get(60)
        except TimeoutError:
            pass
        except KeyboardInterrupt:
            p.terminate()
            err("Terminating pool. ")
            return False
