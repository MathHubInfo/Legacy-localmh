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

import os.path

from lmh.lib.io import err
from lmh.lib.env import install_dir, which
from lmh.lib.config import get_config

# Define all the external tools

"""The path to the svn executable """
svn_executable = get_config("env::svn")

# Find it yourself if the config is empty
if svn_executable == "":
	svn_executable = which("svn")

"""The path to the git executable """
git_executable = get_config("env::git")

# Find it yourself if the config is empty
if git_executable == "":
	git_executable = which("git")

"""The path to the pdflatex executable. """
pdflatex_executable = get_config("env::pdflatex")

if pdflatex_executable == "":
	pdflatex_executable =  which("pdflatex")

"""The path to the perl executable. """
perl_executable = get_config("env::perl")

if perl_executable == "":
	perl_executable =  which("perl")

"""The path to the cpanm executable. """
cpanm_executable = get_config("env::cpanm")

if cpanm_executable == "":
	cpanm_executable =  which("cpanm")

"""The path to the make executable. """
make_executable = get_config("env::make")

if make_executable == "":
	make_executable =  which("make")

"""The path to the tar executable. """
tar_executable = get_config("env::tar")

if tar_executable == "":
	tar_executable =  which("tar")

def check_deps():
	"""Check if dependencies exist. """

	if svn_executable == None:
		err("Unable to locate the subversion executable 'svn'. ")
		err("Please make sure it is in the $PATH environment variable. ")
		err("On a typical Ubuntu system you may install this with:")
		err("    sudo apt-get install subversion")
		return False

	if git_executable == None:
		err("Unable to locate the git executable. ")
		err("Please make sure it is in the $PATH environment variable. ")
		err("On a typical Ubuntu system you may install this with:")
		err("    sudo apt-get install git")
		return False

	if pdflatex_executable == None:
		err("Unable to locate latex executable 'pdflatex'. ")
		err("Please make sure it is in the $PATH environment variable. ")
		err("It is recommened to use TeXLive 2013 or later. ")
		err("On Ubtuntu 13.10 or later you can install this with: ")
		err("    sudo apt-get install texlive")
		err("For older Ubtuntu versions please see: ")
		err("    http://askubuntu.com/a/163683")
		return False

	if perl_executable == None:
		err("Unable to locate perl executable. ")
		err("Please make sure it is in the $PATH environment variable. ")
		err("On Ubtuntu 13.10 or later you can install this with: ")
		err("    sudo apt-get install perl")
		return False

	if cpanm_executable == None:
		err("Unable to locate cpanm executable. ")
		err("Please make sure it is in the $PATH environment variable. ")
		err("On Ubtuntu 13.10 or later you can install this with: ")
		err("    sudo apt-get install cpanminus")
		return False

	if make_executable == None:
		err("Unable to locate make. ")
		err("Please make sure it is in the $PATH environment variable. ")
		return False

	if tar_executable == None:
		err("Unable to locate tar. ")
		err("Please make sure it is in the $PATH environment variable. ")
		return False


	try:
		import psutil
	except:
		err("Unable to locate python module 'psutil'. ")
		err("Please make sure it is installed. ")
		err("You may be able to install it with: ")
		err("    pip install psutil")
		return False

	return True