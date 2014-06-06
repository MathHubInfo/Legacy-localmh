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

from lmh.lib import shellquote
from lmh.lib.env import install_dir
from lmh.lib.io import std, err, write_file
from lmh.lib.extenv import get_template

all_pathstpl = Template(get_template("localpaths.tpl"))

def gen_localpaths(modules, update, verbose, quiet, workers, nice):
  # general all.tex localpaths.tex generation
  jobs = []
  for mod in modules:
    if mod["type"] == "folder":
      if not update or mod["youngest"] > mod["localpaths_time"]:
        jobs.append(localpaths_gen_job(mod))
  try:
    if verbose:
      std("# localpaths.tex Generation")
      for job in jobs:
        localpaths_gen_dump(job)
    else:
      if not quiet:
        std("LOCALPATHS: Generating", len(jobs), "files. ")
      for job in jobs:
        localpaths_gen_do(job, quiet)
  except Exception as e:
    err("LOCALPATHS generation failed. ")
    err(traceback.format_exc())
    return False

  return True

def localpaths_gen_job(module):
  # store parameters for localpaths.tex job generation
  return (module["localpaths_path"], module["repo"], module["repo_name"])


def localpaths_gen_do(job, quiet, worker=None, cwd="."):
  # run a localpaths.tex job
  (dest, repo, repo_name) = job

  if not quiet:
    std("LOCALPATHS: Generating "+dest)

  text = all_pathstpl.substitute(mathhub=install_dir, repo=repo, repo_name=repo_name)

  write_file(dest, text+"\n")

  if not quiet:
    std("LOCALPATHS: Generated "+dest)

def localpaths_gen_dump(job):
  # dump an localpaths.tex generation jump to STDOUT
  (dest, repo, repo_name) = job

  std("# generate", dest)

  text = all_pathstpl.substitute(mathhub=install_dir, repo=repo, repo_name=repo_name)

  std("echo -n " + shellquote(text)+ " > "+shellquote(dest))
  std("echo > "+shellquote(dest))
