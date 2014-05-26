"""
This file is part of LMH.

LMH is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

LMH is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with LMH.  If not, see <http://www.gnu.org/licenses/>.
"""

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

from lmh.lib import shellquote
from lmh.lib.io import std, err, read_file
from lmh.lib.env import install_dir, latexmlstydir, stexstydir
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

def gen_pdf(modules, update, verbose, quiet, workers, nice, add_bd, pdf_pipe_log, find_modules):
  # general pdf generation
  jobs = []
  for mod in modules:
    if mod["type"] == "file":
      if mod["file_pre"] != None and (not update or mod["file_time"] > mod["pdf_time"]):
        if find_modules:
          std(mod["file"])
        else:
          jobs.append(pdf_gen_job(mod, add_bd, pdf_pipe_log))
  if find_modules:
    return True
  try:
    # check we have pdflatex_executable
    if not os.path.isfile(pdflatex_executable):
      raise Exception("pdflatex_executable is missing, make sure you ran lmh setup. ")

    if verbose:
      std("# pdflatex Generation")

      std("export TEXINPUTS="+TEXINPUTS)

      for job in jobs:
        pdf_gen_dump(job)
    elif workers == 1:
      if not quiet:
        std("PDF: Generating", len(jobs), "files")
      for job in jobs:
        pdf_gen_do_master(job, quiet)
    else:
      std("PDF: Generating", len(jobs), "files with", workers, "workers.")
      pool = multiprocessing.Pool(processes=workers)
      try:
        result = pool.map_async(functools.partial(pdf_gen_do_worker, quiet), jobs).get(9999999)
        try:
          res = result.get(9999999)
        except:
          pass
        res = True
      except KeyboardInterrupt:
        err("PDF: received <<KeyboardInterrupt>>")
        err("PDF: killing worker processes ...")
        pool.terminate()
        err("PDF: Waiting for all processes to finish ...")
        time.sleep(5)
        err("PDF: Done. ")
        res = False
      pool.close()
      pool.join()
      if not quiet:
        std("PDF: All workers have finished ")
      return res
  except Exception as e:
    err("PDF generation failed. ")
    err(traceback.format_exc())
    return False

  return True

def pdf_gen_job(module, add_bd, pdf_pipe_log):
  # store parameters for pdf job generation
  _env = os.environ.copy()
  _env["TEXINPUTS"] = TEXINPUTS
  return (module["file_pre"], module["file_post"], module["mod"], _env, module["file"], module["path"], module["pdf_path"], module["pdf_log"], add_bd, pdf_pipe_log)


def pdf_gen_do_master(job, quiet, wid=""):
  # pdf generation in master process
  (pre, post, mod, _env, file, cwd, pdf_path, pdflog, add_bd, pdf_pipe_log) = job

  if not quiet:
    std("PDF"+wid+": Generating", pdf_path)

  os.chdir(cwd)
  try:
    if pre != None:
      if add_bd:
        text = read_file(pre)
        text += "\\begin{document}"
        text += read_file(mod+".tex")
        text += post
      else:
        text = read_file(pre)
        text += read_file(mod+".tex")
        text += post
      
      if pdf_pipe_log:
        p = Popen([pdflatex_executable, "-jobname", mod, "-interaction", "scrollmode"], cwd=cwd, stdin=PIPE, stdout=sys.stdout, stderr=sys.stderr, env = _env)
        p.stdin.write(text)
        p.stdin = sys.stdin
      else:
        p = Popen([pdflatex_executable, "-jobname", mod], cwd=cwd, stdin=PIPE, stdout=PIPE, stderr=PIPE, env = _env)
        p.stdin.write(text)
    else:
      if pdf_pipe_log:
        p = Popen([pdflatex_executable, file, "-interaction", "scrollmode"], cwd=cwd, stdin=sys.stdin, stdout=sys.stdout, env=_env)
      else:
        p = Popen([pdflatex_executable, file], cwd=cwd, stdout=PIPE, env=_env)
    p.wait()
  except KeyboardInterrupt as k:
    err("PDF"+wid+": KeyboardInterrupt, stopping generation")
    p.terminate()
    p.wait()
    raise k

  # move the log file
  shutil.move(file[:-4]+".log", pdflog)
  
  if not quiet:
    if p.returncode == 0:
      std("PDF"+wid+": Generated", pdf_path)
    else:
      err("PDF"+wid+": Did not generate", pdf_path)
  

def pdf_gen_do_worker(quiet, job):
  wid = multiprocessing.current_process()._identity[0]
  pdf_gen_do_master(job, quiet, wid="["+str(wid)+"]")


def pdf_gen_dump(job):
  # dump an pdf job to stdout
  (pre, post, mod, _env, file, cwd, pdf_path, pdflog, add_bd, pdf_pipe_log) = job

  std("# generate", pdf_path )
  std("cd "+cwd)

  if pre != None:
    if add_bd:
      std("echo \"\\begin{document}\\n\" | cat "+shellquote(pre)+" - "+shellquote(file)+" "+shellquote(post)+" | "+pdflatex_executable+" -jobname " + mod+"-interaction scrollmode")
    else:
      std("cat "+shellquote(pre)+" "+shellquote(file)+" "+shellquote(post)+" | "+pdflatex_executable+" -jobname " + mod+ "-interaction scrollmode")

  else:
      std(pdflatex_executable+" "+file)
  std("mv "+job+".log "+pdflog)
