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

import subprocess

import sys

from lmh.lib.env import which
from lmh.lib.io import std, err
from lmh.lib.config import get_config
from lmh.lib.extenv import svn_executable

def clone(dest, *arg):
	"""Clones an svn repository repository. """

	args = [svn_executable, "co", "--non-interactive", "--trust-server-cert"]
	args.extend(arg)

	proc = subprocess.Popen(args, stdout=sys.stdout, stderr=subprocess.PIPE, cwd=dest)
	err_msg = proc.communicate()[1]

	if err_msg.find("already exists") != -1:
		return True

	err(err_msg)
	return (proc.returncode == 0)

def pull(dest, *arg):
	"""Pulls an svn repository. """

	args = [svn_executable, "up"]
	args.extend(arg)

	proc = subprocess.Popen(args, stderr=subprocess.PIPE, cwd=dest)
	err_msg = proc.communicate()[1]

	err(err_msg)
	return (proc.returncode == 0)