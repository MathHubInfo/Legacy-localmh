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

import ConfigParser
import os

from . import util

def config_load_content(root, config):
  for fl in ["pre", "post"]:
    if config.has_option("gen", fl):
      file_path = os.path.realpath(os.path.join(root, config.get("gen", fl)))
      config.set("gen", "%s_content"%fl, util.get_file(file_path));

def traverse(root, config):
  files = os.listdir(root)
  print files
  if any(".lmh" in s for s in files):
    newCfg = ConfigParser.ConfigParser()
    newCfg.read(root+"/.lmh")
    config = newCfg
    print "loading config at %s"%root
    config_load_content(root, config)

initConfig = ConfigParser.ConfigParser();

traverse("/home/costea/localmh/MathHub/jucovschi/smglom/source", initConfig)
