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
import traceback

from lmh import util

ignore = re.compile(r'\\verb')
regStrings = [r'\\(guse|gadopt|symdef|abbrdef|symvariant|keydef|listkeydef|importmodule|gimport|adoptmodule|importmhmodule|adoptmhmodule)', r'\\begin{(module|importmodulevia)}', r'\\end{(module|importmodulevia)}']
regs = map(re.compile, regStrings)

def gen_sms(modules, update, verbose, quiet, workers, nice, find_modules):
  # general sms generation
  jobs = []
  for mod in modules:
    if mod["type"] == "file":
      if not update or mod["file_time"] > mod["sms_time"]:
        if find_modules:
          print module["file"]
        else:
          jobs.append(sms_gen_job(mod))
  if find_modules:
    return True
  try:
    if verbose:
      print "# SMS Generation"
      for job in jobs:
        sms_gen_dump(job)
    else:
      if not quiet:
        print "SMS: Generating", len(jobs), "files"
      for job in jobs:
        sms_gen_do(job, quiet)
  except Exception as e:
    print "SMS generation failed. "
    print traceback.format_exc()
    return False

  return True

def sms_gen_job(module):
  # store parameters for sms job generation
  return (module["file"], module["sms"])

def sms_gen_do(job, quiet, worker=None, cwd="."):
  # run a sms generation job 
  (input, out) = job

  if not quiet:
    print "SMS: Generating ", os.path.relpath(out, cwd)

  output = open(out, "w")

  for line in open(input):
    idx = line.find("%")
    if idx == -1:
      line = line[0:idx];

    if ignore.search(line):
      continue

    for reg in regs:
      if reg.search(line):
        text = line.strip()+"%\n"
        output.write(text)
        break
  
  output.close()

  if not quiet:
    print "SMS: Generated ", os.path.relpath(out, cwd)

def sms_gen_dump(job):
  # dump an sms generation jump to STDOUT
  (input, out) = job

  print "# generate ", out
  print "echo -n '' > "+util.shellquote(out)

  for line in open(input):
    idx = line.find("%")
    if idx == -1:
      line = line[0:idx];

    if ignore.search(line):
      continue

    for reg in regs:
      if reg.search(line):
        text = line.strip()+"%\n"
        print "echo -n "+util.shellquote(text)+" >> "+util.shellquote(out)
        break