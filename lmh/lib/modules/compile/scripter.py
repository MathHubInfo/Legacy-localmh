from lmh.lib.modules.compile.targets import SMSTarget, OMDOCTarget, PDFTarget
from lmh.lib.modules import get_build_groups
from lmh.lib.repos.local.dirs import find_repo_dir
from lmh.lib.repos.local.package import get_package_id
from multiprocessing import current_process

def make_build_script(rgroup, targets, quiet, worker_id):
    (rdir, files) = rgroup

    # grab the package id
    repo = get_package_id(rdir)

    # if we are quiet, do not log user and error.
    if quiet:
        script = "log- user ; log- error ; log console"
    else:
        script = "log console"

    script = script + " ; archive add "+find_repo_dir(rdir)

    # TODO: Create this
    # by having system-wide memory somewhere
    for (t, props) in targets.items():
        if t == "list":
            continue
        props["worker_base"] = 3340
        props["worker_id"] = worker_id
        if t == "sms":
            script = script + " ; " + SMSTarget().build_command(repo, files, props)
        if t == "omdoc":
            script = script + " ; " + OMDOCTarget().build_command(repo, files, props)
        if t == "pdf":
            script = script + " ; " + PDFTarget().build_command(repo, files, props)
    return script
