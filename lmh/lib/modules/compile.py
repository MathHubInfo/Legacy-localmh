from . import get_build_groups
from lmh.lib.repos.local.dirs import find_repo_dir
from lmh.lib.mmt import run
from lmh.lib.io import std
import os

class Target():
    def __init__(self):
        pass
    def getExtension(self):
        pass
    def getTarget(self):
        pass
    def getEnvironment(self, args):
        return {}
    def build_command(self, repo, targets, args):
        script = "extension "+self.getExtension()
        #script = script + " ; " + " ; ".join(["envvar "+k+" \""+v+"\"" for (k, v) in self.getEnvironment(args).iteritems()])
        script = script + " ; " + " ; ".join(["build "+repo+" "+self.getTarget()+" "+t for t in targets])
        return script

class SMSTarget(Target):
    def __init__(self):
        pass
    def getExtension(self):
        return "info.kwarc.mmt.stex.SmsGenerator"
    def getTarget(self):
        return "sms"

def make_build_script(rgroup, targets):
    (repo, files) = rgroup

    script = "log console ; archive add "+find_repo_dir(repo)

    for (t, args) in targets.iteritems():
        if t == "sms":
            script = script + " ; " + SMSTarget().build_command(repo, files, args)

    return (repo, script)

def make_build_scripts(spec, targets):
    return [make_build_script(rgroup, targets) for rgroup in get_build_groups(spec)]

def run_mmt(spec, targets):
    # build the script
    (repo, script) = make_build_script(spec, targets)
    std("Generating targets", " ".join(targets.keys()), "in repository", repo)
    return run([script], path=find_repo_dir(repo))

def run_build(spec, targets):
    return [run_mmt(rgroup, targets) for rgroup in get_build_groups(spec)]
