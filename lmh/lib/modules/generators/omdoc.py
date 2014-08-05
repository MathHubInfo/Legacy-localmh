from . import Generator

import os
import re
import sys
import signal
import time
import traceback
import functools
import multiprocessing

from subprocess import Popen
from subprocess import PIPE

from lmh.lib.config import get_config
from lmh.lib.io import std, err
from lmh.lib.env import install_dir, stexstydir, which
from lmh.lib.extenv import perl5bindir, perl5libdir, perl5env

if get_config("setup::cpanm::selfcontained"):
  latexmlc = install_dir+"/ext/perl5lib/bin/latexmlc"
else:
  latexmlc = which("latexmlc")
stydir = install_dir+"/sty"

class generate(Generator):
    def __init__(self, quiet, **config):
        self.supportsMoreThanOneWorker = True
        self.quiet = quiet
        self.prefix = "OMDOC"
    def needs_file(self, module, gen_mode, text=None):
        if module["type"] != "file":
            return False
        if gen_mode == "force" or gen_mode == "update_log" or gen_mode == "grep_log":
            return True
        elif module["file_time"] > module["omdoc_time"]:
            return True
        else:
            return False
        return False
    def make_job(self, module):
        # store parameters for all.tex job generation

        if module["file_pre"] != None:
            args = [latexmlc, "--profile", "stex-module", "--path="+stydir, module["file"], "--destination="+module["omdoc_path"], "--log="+module["omdoc_log"]]
            args.append("--preamble="+module["file_pre"])
            args.append("--postamble="+module["file_post"])
        else:
            args = [latexmlc, "--profile", "stex", "--path="+stydir, module["file"], "--destination="+module["omdoc_path"], "--log="+module["omdoc_log"]]

        _env = os.environ.copy()
        _env = perl5env(_env)

        return (args, module["omdoc_path"], module["path"], _env)

    def run_job(self,job,worker_id):
        (args, mod, path, _env) = job

        if worker_id == None:
            worker_id = 0

        port = worker_id+3535

        args.extend(["--expire=10", "--port="+str(port)])

        try:
            if self.quiet:
                p = Popen(args, cwd=path, env=_env, stdin=None, stdout=PIPE, stderr=PIPE, bufsize=1)
            else:
                p = Popen(args, cwd=path, env=_env, stdin=None, stdout=sys.stdout, stderr=sys.stderr, bufsize=1)
                p.wait()
        except KeyboardInterrupt as k:
          p.terminate()
          p.wait()
          raise k

        return p.returncode == 0
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
        return m["omdoc_path"]
