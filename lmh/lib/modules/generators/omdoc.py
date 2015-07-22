from . import Generator

import os
import os.path
import re
import sys

from subprocess import Popen
from subprocess import PIPE

from lmh.lib.config import get_config, read_file
from lmh.lib.io import std
from lmh.lib.env import install_dir, stexstydir, which
from lmh.lib.extenv import perl5bindir, perl5libdir, perl5env, latexmlc_executable
from lmh.lib.modules import needsRegen, needsPreamble

latexmlc = latexmlc_executable

stydir = install_dir+"/sty"

successRegex = r"Wrote (.*)(?:$|\n)"

class generate(Generator):
    def __init__(self, quiet, **config):
        self.supportsMoreThanOneWorker = True
        self.quiet = quiet
        self.prefix = "OMDOC"
    def needs_file(self, module, gen_mode, text=None):
        if module["type"] != "file":
            return False
        # No omdoc for localpaths.tex, all.tex and all.*.tex
        if module["mod"] == "localpaths" or module["mod"] == "all" or module["mod"].startswith("all."):
          return False
        if gen_mode == "force":
            return True
        elif gen_mode == "update":
            return needsRegen(module["path"], module["omdoc"])
        elif gen_mode == "update_log":
            return needsRegen(module["path"], module["omdoc_log"])
        elif gen_mode == "grep_log":
            logfile = module["omdoc_log"]
            if not os.path.isfile(logfile):
                return False
            r = text.match(read_file(logfile))
            return True if r else False
        else:
            return False
        return False
    def make_job(self, module):
        # store parameters for all.tex job generation

        # Only check here if we need the preamble
        if needsPreamble(module["file"]) != None:
            args = [latexmlc, "--profile", "stex-module", "--path="+stydir, module["file"], "--destination="+module["omdoc"], "--log="+module["omdoc_log"]]
            args.append("--preamble="+module["file_pre"])
            args.append("--postamble="+module["file_post"])
        else:
            args = [latexmlc, "--profile", "stex", "--path="+stydir, module["file"], "--destination="+module["omdoc"], "--log="+module["omdoc_log"]]

        _env = os.environ.copy()
        _env = perl5env(_env)

        return (args, module["omdoc"], module["path"], _env)

    def run_job(self,job,worker_id):
        (args, mod, path, _env) = job

        res = False

        if worker_id == None:
            worker_id = 0

        port = worker_id+3535

        args.extend(["--expire=10", "--port="+str(port)])
        try:
            p = Popen(args, cwd=path, env=_env, stdin=None, stdout=PIPE, stderr=PIPE, bufsize=1)
            p.wait()

            (s, e) = p.communicate()

            if mod in re.findall(successRegex, e):
                res = True


            if not self.quiet:
                sys.stdout.write(s)
                sys.stderr.write(e)

        except KeyboardInterrupt as k:
            try:
                p.terminate()
                p.wait()
            except:
                pass
            raise k

        return res and p.returncode == 0
    def dump_init(self):
        std("# OMDOC Generation")
        std("export STEXSTYDIR=\""+stexstydir+"\"")
        std("export PATH=\""+perl5bindir+"\":$PATH")
        std("export PERL5LIB=\""+perl5libdir+"\":$PERL5LIB")
        return True
    def dump_job(self, job):
        (args, omdoc, path, env) = job

        std("# generate", omdoc)

        args.extend(["--expire=10", "--port=3353"])

        std("cd "+path)
        std(" ".join(args))

        return True
    def get_log_name(self, m):
        return m["omdoc"]
