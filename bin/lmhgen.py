"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: lmhgen
   :func: create_parser
   :prog: lmhgen

"""

import argparse
import lmhutil
import os
import glob
import functools
from subprocess import call
from subprocess import Popen
from subprocess import PIPE

import re
import time
import datetime
from string import Template
import ConfigParser

from multiprocessing import Pool
import multiprocessing 

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Generation tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers):
  parser_status = subparsers.add_parser('gen', formatter_class=argparse.RawTextHelpFormatter, help='updates generated content')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('repository', type=lmhutil.parseRepo, nargs='*', help="a list of repositories for which to show the status. ").completer = lmhutil.autocomplete_mathhub_repository
  parser.add_argument('-f', '--force', const=True, default=False, action="store_const", help="force all regeneration")
  parser.add_argument('-v', '--verbose', const=True, default=False, action="store_const", help="verbose mode")
  parser.add_argument('--omdoc', nargs="*", help="generate omdoc files")
  parser.add_argument('--pdf', nargs="*", help="generate pdf files")
  parser.epilog = """
Repository names allow using the wildcard '*' to match any repository. It allows relative paths. 
  Example:  
    */*       - would match all repositories from all groups. 
    mygroup/* - would match all repositories from group mygroup
    .         - would be equivalent to "git status ."
""";

#\begin{module}....
#\end{module}
#\begin{importmodulevia}...
#\end{importmodulevia}

#\symdef...
#\abbrdef...
#\symvariant...
#keydef
#\listkeydef
#\importmodule...
#\gimport...
#\adoptmodule...
#\importmhmodule
#\adoptmhmodule

ignore = re.compile(r'\\verb')

regStrings = [r'\\(guse|gadopt|symdef|abbrdef|symvariant|keydef|listkeydef|importmodule|gimport|adoptmodule|importmhmodule|adoptmhmodule)', r'\\begin{(module|importmodulevia)}', r'\\end{(module|importmodulevia)}']
regs = map(re.compile, regStrings)

all_textpl = Template(lmhutil.get_template("alltex_struct.tpl"))
all_modtpl = Template(lmhutil.get_template("alltex_mod.tpl"))
all_pathstpl = Template(lmhutil.get_template("localpaths.tpl"))
lmh_root = lmhutil.lmh_root()
special_files = {"all.tex":True, "localpaths.tex": True};

latexmlc = lmhutil.which("latexmlc")
pdflatex = lmhutil.which("pdflatex")

stexstydir = lmh_root+"/ext/sTeX/sty";
stydir = lmh_root+"/sty";

def genTEXInputs():
  res = ".:"+stydir+":";
  for (root, files, dirs) in os.walk(stexstydir):
    res += root+":"
  return res

TEXINPUTS = genTEXInputs()

def genOMDoc(root, mod, pre_path, post_path, args=None, port=3354):
  print "generating %r"%(mod+".omdoc")
  args = [latexmlc,"--expire=120", "--port="+str(port), "--profile", "stex-module", "--path="+stydir, "--preload="+pre_path, mod+".tex", "--destination="+mod+".omdoc", "--log="+mod+".ltxlog"];
  _env = os.environ;
  _env["STEXSTYDIR"]=stexstydir;
  call(args, cwd=root, env=_env)

def genPDF(root, mod, pre_path, post_path, args=None, port=None):
  print "generating %r"%(mod+".pdf")
  modPath = os.path.join(root, mod);
  p0 = Popen(["echo", "\\begin{document}\n"], stdout=PIPE);
  c1 = ["cat", pre_path, "-", modPath+".tex", post_path];
  p1 = Popen(c1, cwd=root, stdin=p0.stdout, stdout=PIPE);
  p2 = Popen([pdflatex, "-jobname", mod], cwd=root, stdin=p1.stdout, stdout=PIPE, env = {"TEXINPUTS" : TEXINPUTS})
  output = p2.communicate()[0]
  if args and args.verbose:
    print output
  lmhutil.set_file(modPath+".clog", output)

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
  mods = [];
  for file in files:
    if not file.endswith(".tex") or file in special_files:
      continue
    if not os.access(file, os.R_OK): # ignoring files I cannot read
      continue
    
    fullFile = root+"/"+file;
    mods.append({ "modName" : file[:-4], "file": fullFile, "date": os.path.getmtime(fullFile)})
  return mods

def do_compute(fnc, args, omdoc):
  current = multiprocessing.current_process()
  wid = current._identity[0]
  print str(datetime.datetime.now().time())+" worker "+str(wid)+": "+omdoc["modName"]+" "
  fnc(omdoc["root"], omdoc["modName"], omdoc["pre"], omdoc["post"], port=3353+wid, args=args)

def do_bulk_generation(docs, fnc, args):
  if len(docs) < 10:
    for doc in docs:
      fnc(doc["root"], doc["modName"], doc["pre"], doc["post"], args=args)
    return

  processes = 8;

  pool = Pool(processes=processes)
  result = pool.map(functools.partial(do_compute, fnc, args), docs)

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
      config.set("gen", "%s_content"%fl, lmhutil.get_file(file_path));

def gen_ext(extension, root, mods, config, args, todo, force):
  if len(args) == 0:
    for mod in mods:
      modName = mod["modName"]
      modFile = root+"/"+modName+"."+extension;

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
  print "generating in repository %r"%rep
  rep_root = lmhutil.git_root_dir(rep);
  repo_name = lmhutil.lmh_repos(rep)
  omdocToDo = [];
  pdfToDo = [];

  def traverse(root, config):
    files = os.listdir(root)
    if any(".lmh" in s for s in files):
      newCfg = ConfigParser.ConfigParser()
      newCfg.read(root+"/.lmh")
      config = newCfg
      print "loading config at %s"%root
      config_load_content(root, config)

    mods = get_modules(root, files)
    if len(mods) > 0:
      youngest = max(map(lambda x : x["date"], mods))
      gen_sms(root, mods, args)

      allTex = root+"/all.tex";
      localPathTex = root+"/localpaths.tex"
       
      if args.force or not os.path.exists(localPathTex) or youngest > os.path.getmtime(localPathTex):
        genLocalPaths(localPathTex, rep_root, repo_name);

      if args.force or not os.path.exists(allTex) or youngest > os.path.getmtime(allTex):
        genAllTex(allTex, mods, config);

      if args.omdoc != None:
        if config.has_option("gen", "pre_content"):
          gen_ext("omdoc", root, mods, config, args.omdoc, omdocToDo, args.force);
        else:
          print "WARNING: OMDoc generation desired but could not find preamble and/or postamble - skipping generation"

      if args.pdf != None:
        if config.has_option("gen", "pre_content"):
          gen_ext("pdf", root, mods, config, args.pdf, pdfToDo, args.force);
        else:
          print "WARNING: PDF generation desired but could not find preamble and/or postamble - skipping generation"

    for dir in filter((lambda x: os.path.isdir(root+"/"+x)), files):
      traverse(root+"/"+dir, config)

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

  do_bulk_generation(omdocToDo, genOMDoc, args)
  do_bulk_generation(pdfToDo, genPDF, args)

def do(args):
  if len(args.repository) == 0:
    args.repository = [lmhutil.tryRepo(".", lmhutil.lmh_root()+"/MathHub/*/*")]
  for repo in args.repository:
    for rep in glob.glob(repo):
      do_gen(rep, args);