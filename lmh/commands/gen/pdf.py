#!/usr/bin/env python

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

from lmh import util

lmh_root = util.lmh_root()

pdflatex = util.which("pdflatex")
latexmlstydir = lmh_root+"/ext/sTeX/LaTeXML/lib/LaTeXML/texmf"
stydir = lmh_root+"/sty"

# pdf inputs
def genTEXInputs():
  res = ".:"+stydir+":";
  for (root, files, dirs) in os.walk(util.stexstydir):
    res += root+":"
  for (root, files, dirs) in os.walk(util.latexmlstydir):
    res += root+":"
  return res

TEXINPUTS = genTEXInputs()

def gen_pdf(modules, update, verbose, quiet, workers, nice, add_bd, find_modules):
  # general pdf generation
  jobs = []
  for mod in modules:
    if mod["type"] == "file":
      if mod["file_pre"] != None and (not update or mod["file_time"] > mod["pdf_time"]):
        if find_modules:
          print mod["file"]
        else:
          jobs.append(pdf_gen_job(mod, add_bd))
  if find_modules:
    return True
  try:
    # check we have pdflatex
    if not os.path.isfile(pdflatex):
      raise Exception("pdflatex is missing, make sure you ran lmh setup. ")

    if verbose:
      print "# PDFLATEX Generation"

      print "export TEXINPUTS="+TEXINPUTS

      for job in jobs:
        pdf_gen_dump(job)
    elif workers == 1:
      if not quiet:
        print "PDF: Generating", len(jobs), "files"
      for job in jobs:
        pdf_gen_do_master(job, quiet)
    else:
      print "PDF: Generating", len(jobs), "files with", workers, "workers."
      pool = multiprocessing.Pool(processes=workers)
      try:
        result = pool.map_async(functools.partial(pdf_gen_do_worker, quiet), jobs).get(9999999)
        try:
          res = result.get(9999999)
        except:
          pass
        res = True
      except KeyboardInterrupt:
        print "PDF: received <<KeyboardInterrupt>>"
        print "PDF: killing worker processes ..."
        pool.terminate()
        print "PDF: Waiting for all processes to finish ..."
        time.sleep(5)
        print "PDF: Done. "
        res = False
      pool.close()
      pool.join()
      if not quiet:
        print "PDF: All workers have finished "
      return res
  except Exception as e:
    print "PDF generation failed. "
    print traceback.format_exc()
    return False

  return True

def pdf_gen_job(module, add_bd):
  # store parameters for pdf job generation
  _env = os.environ.copy()
  _env["TEXINPUTS"] = TEXINPUTS
  return (module["file_pre"], module["file_post"], module["mod"], _env, module["file"], module["path"], module["pdf_path"], module["pdf_log"], add_bd)


def pdf_gen_do_master(job, quiet, wid=""):
  # pdf generation in master process
  (pre, post, mod, _env, file, cwd, pdf_path, pdflog, add_bd) = job

  if not quiet:
    print "PDF"+wid+": Generating", pdf_path

  args = [pdflatex, "-jobname", mod]

  try:
    if pre != None:
      if add_bd:
        p0 = Popen(["echo", "\\begin{document}\n"], stdout=PIPE)
        c1 = ["cat", pre, "-", mod+".tex", post]
        p1 = Popen(c1, cwd=cwd, stdin=p0.stdout, stdout=PIPE)
      else:
        c1 = ["cat", pre, mod+".tex", post]
        p1 = Popen(c1, cwd=cwd, stdin=None, stdout=PIPE)
      
      p = Popen([pdflatex, "-jobname", mod], cwd=cwd, stdin=p1.stdout, stdout=PIPE, stderr=PIPE, env = _env)
    else:
      p = Popen([pdflatex, file], cwd=cwd, stdout=PIPE, env=_env)
    p.wait()
  except KeyboardInterrupt as k:
    print "PDF"+wid+": KeyboardInterrupt, stopping generation"
    p.terminate()
    p.wait()
    raise k

  # move the log file
  shutil.move(file[:-4]+".log", pdflog)
  
  if not quiet:
    if p.returncode == 0:
      print "PDF"+wid+": Generated", pdf_path
    else:
      print "PDF"+wid+": Did not generate", pdf_path
  

def pdf_gen_do_worker(quiet, job):
  wid = multiprocessing.current_process()._identity[0]
  pdf_gen_do_master(job, quiet, wid="["+str(wid)+"]")


def pdf_gen_dump(job):
  # dump an pdf job to stdout
  (pre, post, mod, _env, file, cwd, pdf_path, pdflog, add_bd) = job

  print "# generate", pdf_path  
  print "cd "+cwd

  if pre != None:
    if add_bd:
      print "echo \"\\begin{document}\\n\" | cat "+util.shellquote(pre)+" - "+util.shellquote(file)+" "+util.shellquote(post)+" | "+pdflatex+" -jobname " + mod
    else:
      print "cat "+util.shellquote(pre)+" "+util.shellquote(file)+" "+util.shellquote(post)+" | "+pdflatex+" -jobname " + mod

  else:
      print pdflatex+" "+file
  print "mv "+job+".log "+pdflog
