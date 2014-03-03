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
import re
import sys
import signal
import time
import traceback
import functools
import multiprocessing

from subprocess import Popen
from subprocess import PIPE

from lmh import util

lmh_root = util.lmh_root()

latexmlc = lmh_root+"/ext/perl5lib/bin/latexmlc"
stydir = lmh_root+"/sty"

# For Error parsing
errorMsg = re.compile("Error:(.*)")
fatalMsg = re.compile("Fatal:(.*)")

def parseLateXMLOutput(file):
  mod = file[:-4]
  logfile = mod+".ltxlog"

  for idx, line in enumerate(open(logfile)):
    m = errorMsg.match(line)
    if m:
      agg.log_error(["compile", "omdoc", "error"], file, m.group(1))
    m = fatalMsg.match(line)
    if m:
      agg.log_error(["compile", "omdoc", "error"], file, m.group(1))


def gen_omdoc(modules, update, verbose, quiet, workers, nice, find_modules):
  # general omdoc generation
  jobs = []
  for mod in modules:
    if mod["type"] == "file":
      if mod["file_pre"] != None and (not update or mod["file_time"] > mod["omdoc_time"]):
        if find_modules:
          print mod["file"]
        else:
          jobs.append(omdoc_gen_job(mod))
  if find_modules:
    return True
  try:
    # check we have latexmlc
    if not os.path.isfile(latexmlc):
      raise Exception("latexmlc is missing, make sure you ran lmh setup. ")

    if verbose:
      print "# OMDOC Generation"

      print "export STEXSTYDIR=\""+util.stexstydir+"\""
      print "export PATH=\""+util.perl5bindir+"\":$PATH"
      print "export PERL5LIB=\""+util.perl5libdir+"\":$PERL5LIB"

      for job in jobs:
        omdoc_gen_dump(job)
    elif workers == 1:
      if not quiet:
        print "OMDOC: Generating", len(jobs), "files"
      for job in jobs:
        omdoc_gen_do_master(job, quiet)
    else:
      print "OMDOC: Generating", len(jobs), "files with", workers, "workers."
      pool = multiprocessing.Pool(processes=workers)
      try:
        result = pool.map_async(functools.partial(omdoc_gen_do_worker, quiet), jobs).get(9999999)
        try:
          res = result.get(9999999)
        except:
          pass
        print res
        res = True
      except KeyboardInterrupt:
        print "OMDOC: received <<KeyboardInterrupt>>"
        print "OMDOC: killing worker processes ..."
        pool.terminate()
        print "OMDOC: Cleaning up latexmls processes ..."
        try:
          p = Popen(['ps', '-A'], stdout=PIPE)
          out, err = p.communicate()
          for line in out.splitlines():
            if 'latexmls' in line:
             pid = int(line.split(None, 1)[0])
             os.kill(pid, signal.SIGKILL)
        except Exception as e:
          print e
          print "OMDOC: Unable to kill some latexmls processes. "
        print "OMDOC: Waiting for all processes to finish ..."
        time.sleep(5)
        print "OMDOC: Done. "
        res = False
      pool.close()
      pool.join()
      if not quiet:
        print "OMDOC: All workers have finished "
      return res
  except Exception as e:
    print "OMDOC generation failed. "
    print traceback.format_exc()
    return False

  return True

def omdoc_gen_job(module):
  # store parameters for omdoc job generation

  args = [latexmlc, "--profile", "stex-module", "--path="+stydir, module["file"], "--destination="+module["omdoc_path"], "--log="+module["omdoc_log"]]
  args.append("--preamble="+module["file_pre"])
  args.append("--postamble="+module["file_post"])

  _env = os.environ.copy()
  _env = util.perl5env(_env)

  return (args, module["omdoc_path"], module["path"], _env)

def omdoc_gen_do_master(job, quiet, port=None, wid=""):
  (args, mod, path, _env) = job

  if port == None:
    port = "3353"

  if not quiet:
    print "OMDOC"+wid+": Generating", mod

  args.extend(["--expire=10", "--port="+str(port)])

  try:
    if quiet:
      p = Popen(args, cwd=path, env=_env, stdin=None, stdout=PIPE, stderr=PIPE, bufsize=1)
    else:
      p = Popen(args, cwd=path, env=_env, stdin=None, stdout=sys.stdout, stderr=sys.stderr, bufsize=1)
    p.wait()
  except KeyboardInterrupt as k:
    print "OMDOC"+wid+": KeyboardInterrupt, stopping generation"
    p.terminate()
    p.wait()
    raise k

  res = False
  try:
    parseLateXMLOutput(mod[:-6]+".tex")
    res = True
  except:
    pass

  if not quiet:
    if p.returncode == 0 and res:
      print "OMDOC"+wid+": Generated", mod
    else:
      print "OMDOC"+wid+": Did not generate", mod

def omdoc_gen_do_worker(quiet, job):
  wid = multiprocessing.current_process()._identity[0]
  omdoc_gen_do_master(job, quiet, port=wid+3353, wid="["+str(wid)+"]")


def omdoc_gen_dump(job):
  # dump an omdoc job to stdout
  (args, omdoc, path, env) = job

  print "# generate", omdoc  

  args.extend(["--expire=10", "--port=3353"])

  print "cd "+path
  print " ".join(args)