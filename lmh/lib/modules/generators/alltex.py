from . import Generator

import os.path

import os
from string import Template

from lmh.lib import shellquote
from lmh.lib.env import install_dir
from lmh.lib.io import std, err, read_file, write_file
from lmh.lib.extenv import get_template

all_modtpl = Template(get_template("alltex_mod.tpl"))
all_textpl = Template(get_template("alltex_struct.tpl"))

class generate(Generator):
    def __init__(self, quiet, **config):
        self.supportsMoreThanOneWorker = True
        self.prefix = "ALLTEX"
    def needs_file(self, module, gen_mode, text=None):
        if module["type"] != "alltex":
            return False
        if gen_mode == "force" or gen_mode == "update_log" or gen_mode == "grep_log":
            return True
        elif module["youngest"] > module["all_time"]:
            return True
        else:
            return False
        return False
    def make_job(self, module):
        # store parameters for all.tex job generation
        pre = read_file(module["pre_file"])
        post = read_file(module["post_file"])
        aux = module["all_file"][:-len("tex")]+"aux"

        return (module["all_file"], aux, pre, post, [m for m in module["mods"] if not (m.startswith("all.") or m == "all" or m == "localpaths")])

    def run_job(self,job,worker_id):
        (dest, aux, pre, post, modules) = job

        try:
            os.remove(aux)
        except:
            pass

        content = [all_modtpl.substitute(file=m) for m in modules]
        text = all_textpl.substitute(pre_tex=pre, post_tex=post, mods="\n".join(content))

        write_file(dest, text+"\n")

        return True
    def dump_job(self, job):
        (dest, aux, pre, post, modules) = job

        std("# generate", dest)

        content = [all_modtpl.substitute(file=m) for m in modules]
        text = all_textpl.substitute(pre_tex=pre, post_tex=post, mods="\n".join(content))

        std("rm", shellquote(aux), "2> /dev/null")
        std("echo -n " + shellquote(text)+ " > "+shellquote(dest))
        std("echo > "+shellquote(dest))

        return True
    def get_log_name(self, m):
        return m["all_file"]
