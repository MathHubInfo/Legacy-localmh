#!/usr/bin/env python

"""
This is the entry point for the Local Math Hub utility. 

.. argparse::
   :module: init
   :func: create_parser
   :prog: init

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
import argparse

from lmh import util
from lmh import config

repoRegEx = '([\w-]+)/([\w-]+)';

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Init tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="init"):
  parser_status = subparsers.add_parser(name, help='initialize repository with MathHub repository structure')
  add_parser_args(parser_status)

def add_parser_args(parser):
  parser.add_argument('--use-git-root', '-g', action="store_const", default=False, const=True, help="initialise repository in the current git repository root. ")


def do(args): 
  if args.use_git_root:
    rootdir = util.git_root_dir()
  else:
    rootdir = os.getcwd()

    if (not (not os.listdir(rootdir))) and (not config.get_config("init::allow_nonempty")):
      print "Could not create repository, directory not empty. "
      print "If you want to enable lmh init on non-empty directories, please run"
      print "    lmh config init::allow_nonempty true"
      print "If you want to use the root of the current git repository, please use lmh install -g"
      return

  metadir = rootdir+"/META-INF"

  tManifest = util.get_template("manifest.tpl")
  tBuild = util.get_template("build.tpl")
  tServe = util.get_template("serve.tpl")

  emptyrepo = util.lmh_root()+"/bin/emptyrepo";
  for root, dirs, files in os.walk(emptyrepo):
    relpath = root[len(emptyrepo):]
    if not os.path.exists("%s%s"%(rootdir,relpath)):
      os.makedirs("%s%s"%(rootdir,relpath))

    for file in files:
      content = util.get_file("%s/1%s"%(root,file))
      util.set_file("%s%s/%s"%(rootdir,relpath,file), content)


  originProp = util.git_origin()
  m = re.search(repoRegEx, originProp)
  if m == None:
    print "Could not detect repository group & name"
    return

  [group, name] = m.group(1, 2)

  if not os.path.exists(metadir+"/MANIFEST.MF"):
    util.set_file(metadir+"/MANIFEST.MF", tManifest.format(group, name))

  if not os.path.exists(rootdir+"/build.msl"):
    util.set_file(rootdir+"/build.msl", tBuild.format(group, name, util.lmh_root()))

  if not os.path.exists(rootdir+"/serve.msl"):
    util.set_file(rootdir+"/serve.msl", tServe.format(group, name, util.lmh_root()))

  print """
  Created new repository successfully. 

  If the new repository depends on other MathHub repositories, we can add them in the line starting with "dependencies:" in META-INF/MANIFEST.MF.

  Note that any changes have to be committed and pushed before the repository can be used by others.
"""
  