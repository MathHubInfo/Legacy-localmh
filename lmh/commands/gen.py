#!/usr/bin/env python

"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: gen
   :func: create_parser
   :prog: gen

"""

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
import re
import glob
import time
import argparse
import datetime
import functools
import ConfigParser
import multiprocessing

from string import Template
from subprocess import call
from subprocess import Popen
from subprocess import PIPE

from lmh import agg
from lmh import util

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Generation tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="gen"):
  parser_status = subparsers.add_parser(name, formatter_class=argparse.RawTextHelpFormatter, help='updates generated content')
  add_parser_args(parser_status)

def add_parser_args(parser):

  flags = parser.add_argument_group("Generation options")

  flags.add_argument('-s', '--simulate', const=True, default=False, action="store_const", help="Instead of running generate commands, output bash-style commands to STDOUT. ")
  flags.add_argument('-f', '--force', const=True, default=False, action="store_const", help="force all regeneration")
  flags.add_argument('-d', '--debug', const=True, default=False, action="store_const", help="verbose mode")
  flags.add_argument('-w', '--workers',  metavar='number', default=8, type=int,
                   help='number of worker processes to use')
  flags.add_argument('-H', '--high', const=False, default=True, dest="low", action="store_const", help="Do not use low priority. ")

  whattogen = parser.add_argument_group("What to generate")

  whattogen.add_argument('--sms', nargs="*", help="generate sms files")
  whattogen.add_argument('--omdoc', nargs="*", help="generate omdoc files")
  whattogen.add_argument('--pdf', nargs="*", help="generate pdf files")

  parser.add_argument('repository', type=util.parseRepo, nargs='*', help="a list of repositories for which to show the generate files. ").completer = util.autocomplete_mathhub_repository
  parser.add_argument('--all', "-a", default=False, const=True, action="store_const", help="generates files for all repositories")
  parser.epilog = """
Repository names allow using the wildcard '*' to match any repository. It allows relative paths. 
  Example:  
    */*       - would match all repositories from all groups. 
    mygroup/* - would match all repositories from group mygroup
    .         - would be equivalent to "git status ."
"""

# the root of lmh
lmh_root = util.lmh_root()

# The special files
special_files = {"all.tex":True, "localpaths.tex": True}

# for gen_sms
ignore = re.compile(r'\\verb')
regStrings = [r'\\(guse|gadopt|symdef|abbrdef|symvariant|keydef|listkeydef|importmodule|gimport|adoptmodule|importmhmodule|adoptmhmodule)', r'\\begin{(module|importmodulevia)}', r'\\end{(module|importmodulevia)}']
regs = map(re.compile, regStrings)

# templates
all_pathstpl = Template(util.get_template("localpaths.tpl"))
all_modtpl = Template(util.get_template("alltex_mod.tpl"))
all_textpl = Template(util.get_template("alltex_struct.tpl"))

# PATHS
latexmlc = util.which("latexmlc") or lmh_root+"/ext/LaTeXML/bin/latexmlc"
pdflatex = util.which("pdflatex")

stexstydir = lmh_root+"/ext/sTeX/sty"
latexmlstydir = lmh_root+"/ext/sTeX/LaTeXML/lib/LaTeXML/texmf"
stydir = lmh_root+"/sty"

def needsPreamble(file):
  # echsk if we need to add the premable
  return re.search(r"\\begin(\w)*{document}", util.get_file(file)) == None 

# For Error parsing
errorMsg = re.compile("Error:(.*)")
fatalMsg = re.compile("Fatal:(.*)")

def parseLateXMLOutput(file):
  mod = file[:-4];
  logfile = mod+".ltxlog";
  try:

    for idx, line in enumerate(open(logfile)):
      m = errorMsg.match(line)
      if m:
        agg.log_error(["compile", "omdoc", "error"], file, m.group(1))
      m = fatalMsg.match(line)
      if m:
        agg.log_error(["compile", "omdoc", "error"], file, m.group(1))
  except:
    print "ERROR: Failed to open logfile '"+logfile+"'. "
    print "Make sure latexmlc is working properly. "


def config_load_content(root, config, msg):
  # Load config content
  msg("CONFIG_LOAD_CONTENT: "+root)
  for fl in ["pre", "post"]:
    if config.has_option("gen", fl):
      file_path = os.path.realpath(os.path.join(root, config.get("gen", fl)))
      config.set("gen", "%s_content"%fl, util.get_file(file_path))

def get_modules(root, files, msg):
  # finds all the modules in root
  mods = []
  msg("GET_MODULES: "+root)
  for file in files:
    fullFile = root+"/"+file
    if not file.endswith(".tex") or file in special_files:
      # skip it if it is in special_files
      continue
    msg("FIND_MODULE: Found "+fullFile)
    mods.append({ "modName" : file[:-4], "file": fullFile, "date": os.path.getmtime(fullFile)})
  return mods

def gen_sms_all(root, mods, args, msg):
  # Generate all SMS files
  msg("SMS_GEN_ALL: " + root)
  for mod in mods:
    smsfileName = root+"/"+mod["modName"]+".sms";

    if args.force or not os.path.exists(smsfileName) or mod["date"] > os.path.getmtime(smsfileName):
      gen_sms(args, mod["file"], smsfileName, msg)


def gen_sms(args, input, output, msg):
  # generates a single sms file
  msg("SMS_GEN: " + output)
  if not args.simulate:
    output = open(output, "w")
  else:
    print "# generate "+output
    print "echo -n '' > "+util.shellquote(output)
  
  for line in open(input):
    idx = line.find("%")
    if idx == -1:
      line = line[0:idx];

    if ignore.search(line):
      continue

    for reg in regs:
      if reg.search(line):
        text = line.strip()+"%\n"
        if args.simulate:
          print "echo -n "+util.shellquote(text)+" >> "+util.shellquote(output)
        else:
          output.write(text)
        break
  if not args.simulate:
    output.close()

def gen_localpaths(dest, repo, repo_name, args, msg):
  # generates localpaths.tex
  msg("GEN_LOCALPATHS: "+dest)
  text = all_pathstpl.substitute(mathhub=lmh_root, repo=repo, repo_name=repo_name)
  if args.simulate:
    print "# generate "+dest
    print "echo -n " + util.shellquote(text)+ " > "+util.shellquote(dest)
    return
  output = open(dest, "w")
  output.write(text)
  output.close()

def gen_alltex(dest, mods, config, args, msg):
  # generates all.tex
  if not config.has_option("gen", "pre_content") or not config.has_option("gen", "post_content"):
    return

  msg("GEN_ALLTEX: "+dest)

  preFileContent = config.get("gen", "pre_content")
  postFileContent = config.get("gen", "post_content")
  content = [];
  for mod in mods:
    content.append(all_modtpl.substitute(file=mod["modName"]));

  text = all_textpl.substitute(pre_tex=preFileContent, post_tex=postFileContent, mods="\n".join(content))

  if args.simulate:
    print "echo -n "+util.shellquote(text) + " > "+util.shellquote(dest)
    return

  output = open(dest, "w")
  output.write(text)
  output.close()

def gen_ext(extension, root, mods, config, args, todo, force, msg):
  # find and add files to todo
  if len(args) == 0:
    msg("GEN_EXT_MODS_"+extension.upper()+": "+root)
    for mod in mods:
      modName = mod["modName"]
      modFile = root+"/"+modName+"."+extension

      if force or not os.path.exists(modFile) or os.path.getmtime(mod["file"]) > os.path.getmtime(modFile):
        msg("GEN_EXT_TODO_"+extension.upper()+": "+modFile)
        todo.append({"root": root, "modName": mod["modName"], "pre" : config.get("gen", "pre"), "post" : config.get("gen", "post")})
  else:
    msg("GEN_EXT_ARGS_"+extension.upper()+": "+root)
    for omdoc in args:
      if omdoc.endswith("."+extension):
        omdoc = omdoc[:-len(extension)-1];
      if omdoc.endswith(".tex"):
        omdoc = omdoc[:-4];
      omdoc = os.path.basename(omdoc)
      msg("GEN_EXT_TODO_"+extension.upper()+": "+omdoc)
      todo.append({"root": root, "modName": omdoc, "pre" : config.get("gen", "pre"), "post" : config.get("gen", "post") })

def gen_omdoc_runner(args, omdoc):
  try:
    current = multiprocessing.current_process()
    wid = current._identity[0]
    def msg(m):
      if args.debug:
        print "#"+ m 
    run_gen_omdoc(omdoc["root"], omdoc["modName"], omdoc["pre"], omdoc["post"], msg, port=3353+wid, args=args)
  except Exception as e:
    print "WARNING: Generating OMDoc failed. (Make sure latexml is running)"


def gen_omdoc(docs, args, msg):

  if args.simulate:
    print "#---------------"
    print "# generate omdoc"
    print "#---------------"
    print "export STEXSTYDIR="+util.shellquote(stexstydir)
    for omdoc in docs:
      run_gen_omdoc(omdoc["root"], omdoc["modName"], omdoc["pre"], omdoc["post"], msg, port=3353, args=args)
  else:
    pool = multiprocessing.Pool(processes=args.workers)
    result = pool.map_async(functools.partial(gen_omdoc_runner, args), docs)

def run_gen_omdoc(root, mod, pre_path, post_path, msg, args=None, port=3354):
  msg("GEN_OMDOC: "+ mod + ".omdoc")
  oargs = args
  args = [latexmlc,"--expire=120", "--port="+str(port), "--profile", "stex-module", "--path="+stydir, mod+".tex", "--destination="+mod+".omdoc", "--log="+mod+".ltxlog"];

  if needsPreamble(root+"/"+mod+".tex"):
    args.append("--preload="+pre_path)

  if oargs.simulate:
    print "cd "+util.shellquote(root)
    print " ".join(args)
    return 

  _env = os.environ;
  _env["STEXSTYDIR"]=stexstydir

  call(args, cwd=root, env=_env, stderr=PIPE)
  parseLateXMLOutput(root+"/"+mod+".tex")


def do_gen(rep, args):
  #main generation function

  def msg(m):
    if args.debug:
      print "#"+ m

  # intialise this repository
  rep_root = util.git_root_dir(rep)
  repo_name = util.lmh_repos(rep)

  # have todo lists
  omdocToDo = []
  pdfToDo = []

  def traverse(root, config):
    # traversing a directory
    files = os.listdir(root)

    # go into subdirectories
    for d in filter((lambda x: os.path.isdir(root+"/"+x)), files):
      traverse(root+"/"+d, config)

    msg("TRAVERSE: "+root)

    # load the config files if possible
    if any(".lmh" in s for s in files):
      newCfg = ConfigParser.ConfigParser()
      try:
        newCfg.read(root+"/.lmh")
        config = newCfg
        config_load_content(root, config)
      except:
        print "WARNING: Failed to load config at %s"%root

    # LOAD the modules
    mods = get_modules(root, files, msg)
    
    if len(mods) > 0:
      # find the youngest mod
      youngest = max(map(lambda x : x["date"], mods))

      # generate sms
      gen_sms_all(root, mods, args, msg)

      # find the localpaths and all .tex files
      allTex = root+"/all.tex"
      localPathTex = root+"/localpaths.tex"
         
      if args.force or not os.path.exists(localPathTex) or youngest > os.path.getmtime(localPathTex):
        gen_localpaths(localPathTex, rep_root, repo_name, args, msg)

        if args.force or not os.path.exists(allTex) or youngest > os.path.getmtime(allTex):
          gen_alltex(allTex, mods, config, args, msg)


        if args.omdoc != None:          
          if config.has_option("gen", "pre_content"):
            gen_ext("omdoc", root, mods, config, args.omdoc, omdocToDo, args.force, msg)
          else:
            print "WARNING: GEN_EXT_OMDOC: OMDoc generation desired but could not find preamble and/or postamble - skipping generation"
      
        if args.pdf != None:
          if config.has_option("gen", "pre_content"):
            gen_ext("pdf", root, mods, config, args.pdf, pdfToDo, args.force, msg);
          else:
            print "WARNING: GEN_EXT_PDF: PDF generation desired but could not find preamble and/or postamble - skipping generation"

  # go into the source directory
  if rep == rep_root:
    rep = rep + "/source"

  if not os.path.exists(rep):
    msg("WARNING: Directory does not exist: %r"%rep)
    return


  # create the configuration files
  initConfig = ConfigParser.ConfigParser()
  initConfig.add_section("gen")

  for fl in ["pre", "post"]:
    fn = rep_root+"/lib/%s.tex"%fl
    if os.path.exists(fn):
      msg("ADD_CONFIG: Found '"+fl+"': "+fn)
      initConfig.set("gen", fl, fn)

  # load the configuration
  config_load_content(rep, initConfig, msg)

  # traverse this directory
  traverse(rep, initConfig)

  try:
    if args.low:
      msg("NOTICE: Using low priority")
      util.lowpriority()
  except Exception as e:
    print e
    print "WARNING: Failed to set low priority!"

  # generate all omdoc
  gen_omdoc(omdocToDo, args, msg)

  # generate all pdf
  # do_bulk_generation(pdfToDo, lambda x:x, args, "pdf", msg)

def do(args):
  if len(args.repository) == 0:
    args.repository = [util.tryRepo(".", util.lmh_root()+"/MathHub/*/*")]
  if args.all:
    args.repository = [util.tryRepo(util.lmh_root()+"/MathHub", util.lmh_root()+"/MathHub")]  

  for repo in args.repository:
    for rep in glob.glob(repo):
      do_gen(rep, args)
  agg.print_summary()
