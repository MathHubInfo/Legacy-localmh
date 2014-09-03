from . import Generator

import os
import sys
import signal
import shutil
import time
import traceback
import functools
import multiprocessing

from subprocess import Popen
from subprocess import PIPE

from lmh.lib import shellquote, popen_wait_timeout
from lmh.lib.io import std, err, read_file, write_file
from lmh.lib.env import install_dir, latexmlstydir, stexstydir
from lmh.lib.config import get_config
from lmh.lib.extenv import pdflatex_executable

stydir = install_dir+"/sty"

# pdf inputs
def genTEXInputs():
    res = ".:"+stydir+":";
    for (root, files, dirs) in os.walk(stexstydir):
        res += root+":"
    for (root, files, dirs) in os.walk(latexmlstydir):
        res += root+":"
    return res+":"+latexmlstydir+":"+stexstydir

TEXINPUTS = genTEXInputs()

class generate(Generator):
    def __init__(self, quiet, **config):
        self.supportsMoreThanOneWorker = True
        self.quiet = quiet
        self.add_bd = config["add_bd"]
        self.pdf_pipe_log = config["pdf_pipe_log"]
        self.prefix = "PDF"
    def needs_file(self, module, gen_mode, text=None):
        if module["type"] != "file":
            return False
        if gen_mode == "force":
            return True
        elif gen_mode == "update_log":
            return module["file_time"] > module["pdf_log_time"]
        elif gen_mode == "grep_log":
            logfile = module["pdf_log"]
            if not os.path.isfile(logfile):
                return False
            r = text.match(read_file(logfile))
            return True if r else False
        elif gen_mode == "update":
            return module["file_time"] > module["pdf_time"]
        else:
            return False
        return False
    def make_job(self, module):
        # store parameters for all.tex job generation
        _env = os.environ.copy()
        _env["TEXINPUTS"] = TEXINPUTS

        return (module["file_pre"], module["file_post"], module["mod"], _env, module["file"], module["path"], module["pdf_path"], module["pdf_log"], self.add_bd, self.pdf_pipe_log)

    def run_job(self,job,worker_id):
        # pdf generation in master process
        (pre, post, mod, _env, file, cwd, pdf_path, pdflog, add_bd, pdf_pipe_log) = job

        if worker_id != None:
            prefix = "PDF["+str(worker_id)+"]:"
        else:
            prefix = "PDF:"

        os.chdir(cwd)

        tempfile = mod+".tmp"

        try:
            if pre != None:

                if add_bd:
                    text = read_file(pre)
                    text += "\\begin{document}"
                    text += read_file(mod+".tex")
                    text += read_file(post)
                else:
                    text = read_file(pre)
                    text += read_file(mod+".tex")
                    text += read_file(post)

                # Write into .tmp
                write_file(tempfile, text)

                if pdf_pipe_log:
                    p = Popen([pdflatex_executable, tempfile, "-jobname", mod, "-interaction", "scrollmode"], cwd=cwd, stdin=PIPE, stdout=sys.stdout, stderr=sys.stderr, env = _env)
                else:
                    p = Popen([pdflatex_executable, "-jobname", mod, tempfile, "-halt-on-error"], cwd=cwd, stdin=PIPE, stdout=PIPE, stderr=PIPE, env = _env)
            else:
                if pdf_pipe_log:
                    p = Popen([pdflatex_executable, file, "-interaction", "scrollmode"], cwd=cwd, stdin=sys.stdin, stdout=sys.stdout, env=_env)
                else:
                    p = Popen([pdflatex_executable, file, "-halt-on-error"], cwd=cwd, stdin=PIPE, stdout=PIPE, env=_env)

            timeout = get_config("gen::pdf::timeout")

            if not popen_wait_timeout(p, timeout):
                err(prefix, "Worker did not finish within "+str(timeout)+"s, sending SIGKILL. ")
        except KeyboardInterrupt as k:
            try:
                os.remove(tempfile)
            except:
                pass
            p.terminate()
            p.wait()
            raise k

        try:
            os.remove(tempfile)
        except:
            pass



        # move the log file
        try:
            shutil.move(file[:-4]+".log", pdflog)
        except:
            pass
        return p.returncode == 0

    def dump_init(self):
        std("#PDF Generation")
        std("export TEXINPUTS="+TEXINPUTS)

        return True
    def dump_job(self, job):
        (pre, post, mod, _env, file, cwd, pdf_path, pdflog, add_bd, pdf_pipe_log) = job

        std("# generate", pdf_path )
        std("cd "+cwd)

        if pre != None:
            if add_bd:
                std("echo \"\\begin{document}\\n\" | cat "+shellquote(pre)+" - "+shellquote(file)+" "+shellquote(post)+" | "+pdflatex_executable+" -jobname " + mod+" -interaction scrollmode")
            else:
                std("cat "+shellquote(pre)+" "+shellquote(file)+" "+shellquote(post)+" | "+pdflatex_executable+" -jobname " + mod+ "-interaction scrollmode")

        else:
            std(pdflatex_executable+" "+file)

        std("mv", os.path.join(cwd, mod+".log"), pdflog)

        return True
    def get_log_name(self, m):
        return m["pdf_path"]
