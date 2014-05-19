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

from lmh.lib.self import get_template
from lmh.lib.io import std, err, read_file, write_file

from lmh.lib import shellquote


all_modtpl = Template(get_template("alltex_mod.tpl"))
all_textpl = Template(get_template("alltex_struct.tpl"))

def gen_alltex(modules, update, verbose, quiet, workers, nice):
  """Generates all.tex files"""

  jobs = []
  for mod in modules:
    if mod["type"] == "folder":
      if (not update or mod["youngest"] > mod["alltex_time"]) and mod["file_pre"] != None:
        jobs.append(alltex_gen_job(mod))
  try:
    if verbose:
      std("# all.tex Generation")
      for job in jobs:
        alltex_gen_dump(job)
    else:
      if not quiet:
        std("ALLTEX: Generating", len(jobs), "files. ")
      for job in jobs:
        alltex_gen_do(job, quiet)
  except Exception as e:
    err("ALLTEX generation failed. ")
    err(traceback.format_exc())
    return False

  return True

def alltex_gen_job(module):
  # store parameters for all.tex job generation
  pre = read_file(module["file_pre"])
  post = read_file(module["file_post"])
  return (module["alltex_path"], pre, post, module["modules"])
  

def alltex_gen_do(job, quiet, worker=None, cwd="."):
  # run a all.tex job 
  (dest, pre, post, modules) = job

  if not quiet:
    std("ALLTEX: Generating", dest)

  content = [all_modtpl.substitute(file=m) for m in modules]
  text = all_textpl.substitute(pre_tex=pre, post_tex=post, mods="\n".join(content))

  write_file(dest, text+"\n")

  if not quiet:
    std("ALLTEX: Generated", dest)

def alltex_gen_dump(job):
  # dump an all.tex generation jump to STDOUT
  (dest, pre, post, modules) = job

  std("# generate", dest)
  
  content = [all_modtpl.substitute(file=m) for m in modules]
  text = all_textpl.substitute(pre_tex=pre, post_tex=post, mods="\n".join(content))

  std("echo -n " + shellquote(text)+ " > "+shellquote(dest))
  std("echo > "+shellquote(dest))
