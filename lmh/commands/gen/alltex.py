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

import traceback

from string import Template

from lmh import util

all_modtpl = Template(util.get_template("alltex_mod.tpl"))
all_textpl = Template(util.get_template("alltex_struct.tpl"))

def gen_alltex(modules, update, verbose, quiet, workers, nice, nothing):
  # general all.tex localpaths.tex generation
  jobs = []
  for mod in modules:
    if mod["type"] == "folder":
      if (not update or mod["youngest"] > mod["alltex_time"]) and mod["file_pre"] != None:
        jobs.append(alltex_gen_job(mod))
  try:
    if verbose:
      print "# all.tex Generation"
      for job in jobs:
        alltex_gen_dump(job)
    else:
      if not quiet:
        print "ALLTEX: Generating", len(jobs), "files. "
      for job in jobs:
        alltex_gen_do(job, quiet)
  except Exception as e:
    print "ALLTEX generation failed. "
    print traceback.format_exc()
    return False

  return True

def alltex_gen_job(module):
  # store parameters for all.tex job generation
  return (module["alltex_path"], module["file_pre"], module["file_post"], module["modules"])
  

def alltex_gen_do(job, quiet, worker=None, cwd="."):
  # run a all.tex job 
  (dest, pre, post, modules) = job

  if not quiet:
    print "ALLTEX: Generating "+dest

  content = [all_modtpl.substitute(file=m) for m in modules]
  text = all_textpl.substitute(pre_tex=pre, post_tex=post, mods="\n".join(content))

  output = open(dest, "w")
  output.write(text)
  output.close()

  if not quiet:
    print "ALLTEX: Generated "+dest

def alltex_gen_dump(job):
  # dump an all.tex generation jump to STDOUT
  (dest, pre, post, modules) = job

  print "# generate", dest
  
  content = [all_modtpl.substitute(file=m) for m in modules]
  text = all_textpl.substitute(pre_tex=pre, post_tex=post, mods="\n".join(content))

  print "echo -n " + util.shellquote(text)+ " > "+util.shellquote(dest)
