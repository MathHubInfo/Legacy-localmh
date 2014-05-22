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
import shutil

from lmh.lib.io import std, err, write_file, read_file
from lmh.lib.modules import locate_modules, needsPreamble

def create_parser():
  parser = argparse.ArgumentParser(description='Generates smybols needed by language bindings. ')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="symbols"):
  parser_status = subparsers.add_parser(name, help='Generates smybols needed by language bindings. ')
  add_parser_args(parser_status)

def add_parser_args(parser):
  #parser.add_argument('--simulate', action="store_const", default=False, const=True, help="Simulate only. ")
  pass
  #TODO: Add repository arguments


  parser.epilog = """
      TBD
  """

def pat_to_match(pat , o = 0):
  # turn it into a match

  if pat[3+o] != "":
    split = pat[3+o].split("-")
    if pat[0] == "adef":
      split = split[1:]
    return [pat[0], len(split), split]

  if pat[0] == "adef":
    o += 2

  if pat[1] == "i":
    return [pat[0], 1, [pat[5+o]]]
  elif pat[1] == "ii":
    return [pat[0], 2, [pat[5+o], pat[7+o]]]
  elif pat[1] == "iii":
    return [pat[0], 3, [pat[5+o], pat[7+o], pat[9+o]]]



def find_all_defis(text):
  # find all a?defs and turn them into nice matches
  pattern = r"\\(def|adef)(i{1,3})(\[(.*?)\])?({([^{}]+)?})({([^{}]+)?})?({([^{}]+)?})?({([^{}]+)?})?"
  vals = [pat_to_match(x) for x in re.findall(pattern, text)]
  return vals

def find_all_symis(text):
  # find all the symis
  pattern = r"\\begin{modsig}((.|\n)*)\\end{modsig}"
  pattern2 = r"\\(sym)(i{1,3})(\*)?(\[(.*?)\])?({([^{}]+)?})({([^{}]+)?})?({([^{}]+)?})?"
  matches = re.findall(pattern, text)
  if len(matches) == 0:
    return []
  text = matches[0][0]
  return [pat_to_match(x, o=1) for x in re.findall(pattern2, text)]

def add_symis(text, symis):
  addtext = ""
  for sym in symis:
    addtext += "\\sym"+("i"*sym[1]) +"{"+"}{".join(sym[2])+"}\n"
  pattern = r"\\begin{modsig}((.|\n)*)\\end{modsig}"
  return re.sub(pattern, r"\\begin{modsig}\1"+addtext+"\\end{modsig}", text)



def add_symbols(fname):

  # skip non-language bindings
  languageFilePattern = r"\.(\w+)\.tex$"
  if len(re.findall(languageFilePattern, fname)) == 0:
    return True

  # Find the associated module
  fmodname = re.sub(languageFilePattern, ".tex", fname)
  content = read_file(fname)

  # Try and read the other file
  try:
    modcontent = read_file(fmodname)
  except IOError:
    err("Missing module:", fmodname)
    return False

  # FInd all the symbolds and definitions
  defs = find_all_defis(content)
  syms = find_all_symis(modcontent)

  if defs == None:
    defs = []
  if syms == None:
    syms = []

  # check if we still need them
  def has_syms(d):
    req = ["sym", d[1], d[2]]
    return not (req in syms)

  # OK filter them out
  required = filter(has_syms, defs)

  # Add them if we need to
  if len(required) >= 0:
    std("Adding", len(required), "symbol definition(s) from", fname)
    towrite = add_symis(modcontent, required)
    write_file(fmodname, towrite)

  return True




def do(args):
  # Find all the modules that we have to worry about
  mods = filter(lambda x:x["type"] == "file", locate_modules(os.getcwd()))
  mods = filter(lambda x:needsPreamble(x["file"]), mods)

  ret = True

  for mod in mods:
    ret = ret and add_symbols(mod["file"])

  return