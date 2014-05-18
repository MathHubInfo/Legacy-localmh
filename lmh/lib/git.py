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

import sys
import os.path
import subprocess

from lmh.lib.io import std, err
from lmh.lib.extenv import git_executable


def clone(dest, *arg):
	"""Clones a git repository. """
	args = [git_executable, "clone"]
	args.extend(arg)
	proc = subprocess.Popen(args, stderr=sys.stderr, stdout=sys.stdout, cwd=dest)
	proc.wait()
	return (proc.returncode == 0)

def pull(dest, *arg):
	"""Pulls a git repository. """

	args = [git_executable, "pull"];
	args.extend(arg);
	proc = subprocess.Popen(args, stderr=sys.stderr, stdout=sys.stdout, cwd=dest)
	proc.wait()
	return (proc.returncode == 0)

def push(dest, *arg):
	"""Pulls a git repository. """

	args = [git_executable, "push"];
	args.extend(arg);
	proc = subprocess.Popen(args, stderr=sys.stderr, stdout=sys.stdout, cwd=dest)
	proc.wait()
	return (proc.returncode == 0)

def exists(dest):
	"""Checks if a git repository exists. """
	
	args = [git_executable, "ls-remote", dest]
	proc = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
	proc.wait()
	return (proc.returncode == 0)

def root_dir(dir = "."):
	"""Finds the git root dir of the given path. """
	if os.path.isfile(dir):
		dir = os.path.dirname(dir)

	rootdir = subprocess.Popen([git_executable, "rev-parse", "--show-toplevel"], 
								stdout=subprocess.PIPE,
								cwd=dir,
								).communicate()[0]
	rootdir = rootdir.strip()
	return rootdir

def origin(dir="."):
	"""Finds the origin of a given git repository. """

	return subprocess.Popen([git_executable, "remote", "show", "origin", "-n"], 
							stdout=subprocess.PIPE,
							cwd=rootdir,
							).communicate()[0]