from . import Generator

import os.path

from string import Template

from lmh.lib import shellquote
from lmh.lib.env import install_dir
from lmh.lib.io import std, err, write_file
from lmh.lib.extenv import get_template
from lmh.lib.modules import needsRegen

all_pathstpl = Template(get_template("localpaths.tpl"))

class generate(Generator):
    def __init__(self, quiet, **config):
        self.supportsMoreThanOneWorker = True
        self.prefix = "LOCALPATHS"
    def needs_file(self, module, gen_mode, text=None):
        if module["type"] != "folder":
            return False
        if gen_mode == "force" or gen_mode == "update_log" or gen_mode == "grep_log":
            return True
        elif module["youngest"] > module["localpaths_time"]:
            return True
        else:
            return False
        return False
    def make_job(self, module):
        return (module["localpaths_path"], module["repo"], module["repo_name"])

    def run_job(self,job,worker_id):
        (dest, repo, repo_name) = job

        text = all_pathstpl.substitute(mathhub=install_dir, repo=repo, repo_name=repo_name)
        write_file(dest, text+"\n")

        return True
    def dump_job(self, job):
        (dest, repo, repo_name) = job

        std("# generate", dest)

        text = all_pathstpl.substitute(mathhub=install_dir, repo=repo, repo_name=repo_name)

        std("echo -n " + shellquote(text)+ " > "+shellquote(dest))
        std("echo > "+shellquote(dest))

        return True
    def get_log_name(self, m):
        return os.path.join(m["path"], "localpaths.tex")
