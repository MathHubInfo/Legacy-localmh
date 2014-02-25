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

  flags.add_argument('-s', '--simulate', const=True, default=False, action="store_const", help="Simulate only. Prints all commands to be executed. UNIMPLEMENTED. ")
  flags.add_argument('-f', '--force', const=True, default=False, action="store_const", help="force all regeneration")
  flags.add_argument('-v', '--verbose', const=True, default=False, action="store_const", help="verbose mode")
  flags.add_argument('-w', '--workers',  metavar='number', default=8, type=int,
                   help='number of worker processes to use')
  flags.add_argument('-l', '--low', const=True, default=False, dest="low", action="store_const", help="Use low priority for woker processes. ")

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
""";


ignore = re.compile(r'\\verb')

regStrings = [r'\\(guse|gadopt|symdef|abbrdef|symvariant|keydef|listkeydef|importmodule|gimport|adoptmodule|importmhmodule|adoptmhmodule)', r'\\begin{(module|importmodulevia)}', r'\\end{(module|importmodulevia)}']
regs = map(re.compile, regStrings)

all_textpl = Template(util.get_template("alltex_struct.tpl"))
all_modtpl = Template(util.get_template("alltex_mod.tpl"))
all_pathstpl = Template(util.get_template("localpaths.tpl"))
lmh_root = util.lmh_root()
special_files = {"all.tex":True, "localpaths.tex": True};

latexmlc = util.which("latexmlc")
pdflatex = util.which("pdflatex")

stexstydir = lmh_root+"/ext/sTeX/sty";
latexmlstydir = lmh_root+"/ext/sTeX/LaTeXML/lib/LaTeXML/texmf";
stydir = lmh_root+"/sty";

def genTEXInputs():
  res = ".:"+stydir+":";
  for (root, files, dirs) in os.walk(stexstydir):
    res += root+":"
  for (root, files, dirs) in os.walk(latexmlstydir):
    res += root+":"
  return res

TEXINPUTS = genTEXInputs()

# ---------------- OMDOC generation -----------------------------
errorMsg = re.compile("Error:(.*)")
fatalMsg = re.compile("Fatal:(.*)")

def parseLateXMLOutput(file):
  mod = file[:-4];
  logfile = mod+".ltxlog";

  for idx, line in enumerate(open(logfile)):
    m = errorMsg.match(line)
    if m:
      agg.log_error(["compile", "omdoc", "error"], file, m.group(1))
    m = fatalMsg.match(line)
    if m:
      agg.log_error(["compile", "omdoc", "error"], file, m.group(1))

def needsPreamble(file):
  return re.search(r"\\begin(\w)*{document}", util.get_file(file)) == None 

def genOMDoc(root, mod, pre_path, post_path, args=None, port=3354):
  print "generating %r"%(mod+".omdoc")
  args = [latexmlc,"--expire=120", "--port="+str(port), "--profile", "stex-module", "--path="+stydir, mod+".tex", "--destination="+mod+".omdoc", "--log="+mod+".ltxlog"];

  if needsPreamble(root+"/"+mod+".tex"):
    args.append("--preload="+pre_path)

  _env = os.environ;
  _env["STEXSTYDIR"]=stexstydir;
  call(args, cwd=root, env=_env, stderr=PIPE)
  parseLateXMLOutput(root+"/"+mod+".tex")

def genPDF(root, mod, pre_path, post_path, args=None, port=None):
  print "generating %r"%(mod+".pdf")
  modPath = os.path.join(root, mod);
  if needsPreamble(root+"/"+mod+".tex"):
    p0 = Popen(["echo", "\n"], stdout=PIPE);
    c1 = ["cat", pre_path, "-", modPath+".tex", post_path];
    p1 = Popen(c1, cwd=root, stdin=p0.stdout, stdout=PIPE);
    p2 = Popen([pdflatex, "-jobname", mod], cwd=root, stdin=p1.stdout, stdout=PIPE, env = {"TEXINPUTS" : TEXINPUTS})
  else:
    p2 = Popen([pdflatex, mod+".tex"], cwd=root, stdout=PIPE, env = {"TEXINPUTS" : TEXINPUTS})

  output = p2.communicate()[0]
  if args and args.verbose:
    print output
  util.set_file(modPath+".clog", output)

def genSMS(input, output):
  print "generating %r"%output
  output = open(output, "w")
  for line in open(input):
    idx = line.find("%")
    if idx == -1:
      line = line[0:idx];

    if ignore.search(line):
      continue

    for reg in regs:
      if reg.search(line):
        output.write(line.strip()+"%\n")
        break
  output.close()

def genAllTex(dest, mods, config):
  if not config.has_option("gen", "pre_content") or not config.has_option("gen", "post_content"):
    return
  print "generating %r"%dest

  preFileContent = config.get("gen", "pre_content")
  postFileContent = config.get("gen", "post_content")
  content = [];
  for mod in mods:
    content.append(all_modtpl.substitute(file=mod["modName"]));

  output = open(dest, "w")
  output.write(all_textpl.substitute(pre_tex=preFileContent, post_tex=postFileContent, mods="\n".join(content)))
  output.close()

def genLocalPaths(dest, repo, repo_name):
  print "generating %r"%dest
  output = open(dest, "w")
  output.write(all_pathstpl.substitute(mathhub=lmh_root, repo=repo, repo_name=repo_name))
  output.close()

def get_modules(root, files):
  mods = []
  for file in files:
    fullFile = root+"/"+file
    if not file.endswith(".tex") or file in special_files:
      # skip it if it is in special_files
      continue
    mods.append({ "modName" : file[:-4], "file": fullFile, "date": os.path.getmtime(fullFile)})
  return mods

def do_compute(fnc, args, omdoc):
    current = multiprocessing.current_process()
    wid = current._identity[0]
    try:
      if args.low:
        util.lowpriority()
    except:
      print "Failed to set low priority!"

    print str(datetime.datetime.now().time())+" worker "+str(wid)+": "+omdoc["modName"]+" "
    fnc(omdoc["root"], omdoc["modName"], omdoc["pre"], omdoc["post"], port=3353+wid, args=args)


def do_bulk_generation(docs, fnc, args, ty):
  if args.simulate:
    for doc in docs:
      print ty+": '"+ doc["root"] + doc["modName"]+ "'"
    return

  pool = multiprocessing.Pool(processes=args.workers)
  result = pool.map_async(functools.partial(do_compute, fnc, args), docs)

def gen_sms(root, mods, args):
  # Generate all SMS files
  for mod in mods:
    smsfileName = root+"/"+mod["modName"]+".sms";

    if args.force or not os.path.exists(smsfileName) or mod["date"] > os.path.getmtime(smsfileName):
      genSMS(mod["file"], smsfileName)

def config_load_content(root, config):
  for fl in ["pre", "post"]:
    if config.has_option("gen", fl):
      file_path = os.path.realpath(os.path.join(root, config.get("gen", fl)))
      config.set("gen", "%s_content"%fl, util.get_file(file_path))

def gen_ext(extension, root, mods, config, args, todo, force):
  if len(args) == 0:
    for mod in mods:
      modName = mod["modName"]
      modFile = root+"/"+modName+"."+extension


      if force or not os.path.exists(modFile) or os.path.getmtime(mod["file"]) > os.path.getmtime(modFile):
        todo.append({"root": root, "modName": mod["modName"], "pre" : config.get("gen", "pre"), "post" : config.get("gen", "post")})
  else:
    for omdoc in args:
      if omdoc.endswith("."+extension):
        omdoc = omdoc[:-len(extension)-1];
      if omdoc.endswith(".tex"):
        omdoc = omdoc[:-4];
      omdoc = os.path.basename(omdoc)
      todo.append({"root": root, "modName": omdoc, "pre" : config.get("gen", "pre"), "post" : config.get("gen", "post") })

def do_gen(rep, args):
  #print "generating in repository %r"%rep
  rep_root = util.git_root_dir(rep);
  repo_name = util.lmh_repos(rep)
  omdocToDo = []
  pdfToDo = []

  def traverse(root, config):
    files = os.listdir(root)
    print "Scanning %r"%root

    if any(".lmh" in s for s in files):
      newCfg = ConfigParser.ConfigParser()
      try:
        newCfg.read(root+"/.lmh")
        config = newCfg
        print "loading config at %s"%root
        config_load_content(root, config)
      except:
        print "failed to load config at %s"%root
        print "Skipping config file ..."


    mods = get_modules(root, files)
    if len(mods) > 0:
      youngest = max(map(lambda x : x["date"], mods))
      gen_sms(root, mods, args)

      allTex = root+"/all.tex";
      localPathTex = root+"/localpaths.tex"
       
      if args.force or not os.path.exists(localPathTex) or youngest > os.path.getmtime(localPathTex):
        print "Generating local paths %r"%root
        genLocalPaths(localPathTex, rep_root, repo_name);

      if args.force or not os.path.exists(allTex) or youngest > os.path.getmtime(allTex):
        print "Generating all tex %r"%root
        genAllTex(allTex, mods, config);

      if args.omdoc != None:
        print "Generating omdocs in %r"%root
        if config.has_option("gen", "pre_content"):
          gen_ext("omdoc", root, mods, config, args.omdoc, omdocToDo, args.force);
        else:
          print "WARNING: OMDoc generation desired but could not find preamble and/or postamble - skipping generation"
      if args.pdf != None:
        if config.has_option("gen", "pre_content"):
          print "Generating pdfs in %r"%root
          gen_ext("pdf", root, mods, config, args.pdf, pdfToDo, args.force);
        else:
          print "WARNING: PDF generation desired but could not find preamble and/or postamble - skipping generation"

    for d in filter((lambda x: os.path.isdir(root+"/"+x)), files):
      traverse(root+"/"+d, config)

  if rep == rep_root:
    rep = rep + "/source";

  if not os.path.exists(rep):
    return

  initConfig = ConfigParser.ConfigParser();
  initConfig.add_section("gen");

  for fl in ["pre", "post"]:
    if os.path.exists(rep_root+"/lib/%s.tex"%fl):
      initConfig.set("gen", fl, rep_root+"/lib/%s.tex"%fl);
  config_load_content(rep, initConfig);

  traverse(rep, initConfig)

  do_bulk_generation(omdocToDo, genOMDoc, args, "omdoc")
  do_bulk_generation(pdfToDo, genPDF, args, "pdf")

def do(args):
  if len(args.repository) == 0:
    args.repository = [util.tryRepo(".", util.lmh_root()+"/MathHub/*/*")]
  if args.all:
    args.repository = [util.tryRepo(util.lmh_root()+"/MathHub", util.lmh_root()+"/MathHub")]  

  for repo in args.repository:
    for rep in glob.glob(repo):
      do_gen(rep, args)
  agg.print_summary()
