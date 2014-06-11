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
import shutil

from argparse import Namespace

from lmh.lib.io import std, err
from lmh.lib.env import data_dir

from lmh.lib.repos.local import match_repo_args, find

def find_and_replace_all(search, replace):

	args = Namespace()
	args.__dict__.update({
    "all": True,
    "matcher": search,
    "replace": replace,
    "apply": True,
    "repository": []
  })

	ret = True
	repos = match_repo_args(args.repository, args.all)
	for rep in repos:
		ret = find(rep, args) and ret

	return ret

def movemod(source, dest, modules, simulate = False):
  # change directory to MathHub root, makes paths easier
  if simulate:
    std("cd "+data_dir)
  else:
    os.chdir(data_dir)

  for module in modules:
    # Figure out the full path to the source
    srcpath = source + "/source/" +  module

    # Assemble source paths further
    srcargs = (source + "/" + module).split("/")
    srcapath = "/".join(srcargs[:-1])
    srcbpath = srcargs[-1]

    # Assemble all the commands
    oldcall = "[" + srcapath + "]{"+srcbpath+"}"
    oldcall_long = "[(.*)repos=" + srcapath + "(.*)]{"+srcbpath+"}"
    oldcall_local = "{"+srcbpath+ "}"
    newcall = "[" + dest + "]{"+srcbpath+"}"
    newcall_long = "[$g1" + dest + "$g2]{"+srcbpath+"}"

    dest += "/source/"

    file_patterns = ["", ".de", ".en"]

    # Move the files
    if simulate:
      for pat in file_patterns:
        # try to move the file if it exists
        try:
          std("mv "+srcpath + pat +".tex"+ " "+ dest + " 2>/dev/null || true")
        except:
          pass

    else:
      for pat in file_patterns:
        # try to move the file if it exists
        try:
          shutil.move(srcpath + pat + ".tex", dest)
        except:
          pass


    def run_lmh_find(search, replace, simulate):
      if simulate:
        # simulation
        std("lmh find "+search+" --replace "+replace+" --apply")
        return True
      else:
        # run lmmh find $search --replace $replace --apply
        #main(cmd)
        find_and_replace_all(search, replace)

    # Run all the commands
    m = "("+"|".join(["gimport", "guse", "gadopt"])+")"
    run_lmh_find('\\\\'+m+oldcall, '\\$g0'+newcall, simulate)
    run_lmh_find('\\\\'+m+oldcall_local, '\\$g0'+newcall, simulate)

    m = "("+ "|".join(["importmhmodule", "usemhmodule", "adoptmhmodule", "usemhvocab"]) + ")"
    run_lmh_find('\\'+m+oldcall_long, '\\$g0'+newcall_long, simulate)
    run_lmh_find('\\'+m+oldcall_local, '\\$g0'+newcall_long, simulate)
