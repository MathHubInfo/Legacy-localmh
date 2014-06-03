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
import sys

from lmh.lib.io import std, err
from lmh.lib.env import install_dir, which, stexstydir
from lmh.lib.config import get_config

from subprocess import Popen

import shlex

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

#
# Perl 5 etc
#

if get_config("setup::cpanm::selfcontained"):
	"""The perl5 root directories (if selfcontained)"""
	perl5root = [install_dir+"/ext/perl5lib/", os.path.expanduser("~/")]
else:
	# Perl5 root directory is just global
	perl5root = []

"""Perl5 binary directories"""
perl5bindir = ":".join([p5r+"bin" for p5r in perl5root])+":"+install_dir+"/ext/LaTeXML/bin"+":"+install_dir+"/ext/LaTeXMLs/bin"

"""Perl5 lib directories"""
perl5libdir = ":".join([p5r+"lib/perl5" for p5r in perl5root])+":"+install_dir+"/ext/LaTeXML/blib/lib"+":"+install_dir+"/ext/LaTeXMLs/blib/lib"

def perl5env(_env = {}):
	"""perl 5 environment generator"""
	_env["PATH"]=perl5bindir+":"+_env["PATH"]
	try:
		_env["PERL5LIB"] = perl5libdir+":"+ _env["PERL5LIB"]
	except:
		_env["PERL5LIB"] = perl5libdir
	_env["STEXSTYDIR"] = stexstydir
	return _env


def run_shell(shell = None, args=""):
	"""Runs a shell that is ready for any perl5 things"""

	if shell == None:
		shell = os.environ["SHELL"] or which("bash")
	else:
		shell = which(shell)
		if shell == None:
			return 127

	# Make a perl 5 environment
	_env = perl5env(os.environ)

	try:
		runner = Popen([shell]+shlex.split(args), env=_env, cwd=install_dir, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
	except Exception as e:
		# we could not find that
		return 127

	def do_the_run():
		try:
			runner.wait()
		except KeyboardInterrupt:
			runner.send_signal(signal.SIGINT)
			do_the_run()

	std("Opening a shell ready to compile for you. ")
	do_the_run()

	return runner.returncode