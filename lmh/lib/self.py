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
import shutil
from subprocess import call

from lmh.lib.io import std, err, read_file
from lmh.lib.env import install_dir, ext_dir
from lmh.lib.extenv import perl5env, perl5root
from lmh.lib.extenv import check_deps, cpanm_executable, perl_executable, make_executable
from lmh.lib.config import get_config, set_config
from lmh.lib.git import pull as git_pull
from lmh.lib.git import clone as git_clone
from lmh.lib.svn import pull as svn_pull
from lmh.lib.svn import clone as svn_clone

def update():
	""" Updates lmh codebase. """

	# pull
	std("Updating lmh. ")

	if not git_pull(install_dir):
		err("Update has failed, please check your network connection. ")
		return False

	return True

def update_deps():
	"""Update lmh and its dependencies"""

	std("Updating LMH dependencies ...")

	return run_setup({
		"m_action": "up",
		"force": True,
		"autocomplete": False,
		"latexml_source": "",
		"stex_source": "",
		"mmt_source": "",
		"latexml_action": "",
		"stex_action": "",
		"mmt_action": ""
	})

# Is cpanm selfcontained? Check the config setting
if get_config("setup::cpanm::selfcontained"):
	cpanm_installdeps_args = [cpanm_executable, "-L", perl5root[0], "--installdeps", "--prompt", "."]
	cpanm_installself_args = [cpanm_executable, "-L", perl5root[0], "--notest", "--prompt", "."]
else:
	cpanm_installdeps_args = [cpanm_executable, "--installdeps", "--prompt", "."]
	cpanm_installself_args = [cpanm_executable, "--notest", "--prompt", "."]


#
# General Setup Functions
#

def get_item_source(source_string, def_source, def_branch, name=""):
	"""Gets the source branch and origin from a string and defaults. """
	source = def_source
	branch = def_branch

	if not source_string == "":
		index = source_string.find("@")
		if index == 0:
			branch = source_string[1:]
		elif index > 0:
			source = source_string[:index]
			branch = source_string[index+1:]
		else:
			source = source_string

		std("Using", name, "Version: "+source+"@"+branch)

	return (source, branch)

def cpanm_make(root, name):
	"""Run CPANM make commands for a package. """

	_env = perl5env(os.environ)
	_env.pop("STEXSTYDIR", None)

	try:
		call(cpanm_installdeps_args, env=_env, cwd=root+"/"+name, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
		call(cpanm_installself_args, env=_env, cwd=root+"/"+name, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
		return True
	except Exception as e:
		err("Unable to run make commands for", name, ". ")
		err(e)
		return False

#
# GIT-controlled setups
#

def git_install(root, source, branch, name):
	"""Install a git-controlled software"""

	try:
		if branch == "":
			return git_clone(root, source, name)
		else:
			return git_clone(root, source, "-b", branch, name)
	except:
		err("Failed to install", name, "(is the source available? )")
		return False

def git_update(root, source, branch, name):
	"""Update a git-controlled software"""

	try:
		return git_pull(root + "/" + name)
	except:
		err("Failed to update", name, "(is it present? )")
		return False


def git_remove(root, source, branch):
	"""Update a git-controlled software"""

	try:
		shutil.rmtree(root + "/" + name)
		return True
	except:
		err("Failed to remove", name, "(is it present? )")
		return False

def git_run_setup(name, action, run_cpanm, source_string, ext_dir, def_action, def_source, def_branch):
	"""Runs the setup of an git-based software."""

	action = action or def_action
	(source, branch) = get_item_source(source_string, def_source, def_branch, name=name)

	if action == "re":
		std("Reinstalling", name, "...")
		if not git_remove(ext_dir, source, branch, name):
			return (False, None, None)
		if not git_install(ext_dir, source, branch, name):
			return (False, None, None)
	if action == "in":
		std("Installing", name, "...")
		if not git_install(ext_dir, source, branch, name):
			return (False, None, None)
	if action == "up":
		std("Updating", name, "...")
		if not git_update(ext_dir, source, mmt_branch):
			return (False, None, None)
	if action != "sk" and run_cpanm:
		if not cpanm_make(ext_dir, name):
			return (False, None, None)
	return (True, source, branch)

#
# SVN-controlled setups
#

def svn_install(root, source, branch, name):
	"""Install a svn-controlled software"""

	try:
		if branch == "":
			return svn_clone(root, source, name)
		else:
			return svn_clone(root, source + "@" + branch, name)
	except Exception as e:
		err(e)
		err("Failed to install", name, "(is it present? )")
		return False


def svn_update(root, source, branch, name):
	"""Update a SVN-controlled software"""

	try:
		return svn_pull(root + "/" + name)
	except:
		err("Failed to update", name, "(is it present? )")
		return False

def svn_remove(root, source, branch, name):
	"""Remove a SVN-controlled software"""

	try:
		shutil.rmtree(root + "/MMT")
		return True
	except:
		err("Failed to remove MMT (is it present? )")
		return False

def svn_run_setup(name, action, run_cpanm, source_string, ext_dir, def_action, def_source, def_branch):
	"""Runs the setup of an SVN-based software."""

	action = action or def_action
	(source, branch) = get_item_source(source_string, def_source, def_branch, name=name)

	if action == "re":
		std("Reinstalling", name, "...")
		if not svn_remove(ext_dir, source, branch, name):
			return (False, None, None)
		if not svn_install(ext_dir, source, branch, name):
			return (False, None, None)
	if action == "in":
		std("Installing", name, "...")
		if not svn_install(ext_dir, source, branch, name):
			return (False, None, None)
	if action == "up":
		std("Updating", name, "...")
		if not svn_update(ext_dir, source, branch):
			return (False, None, None)
	if action != "sk" and run_cpanm:
		if not cpanm_make(ext_dir, name):
			return (False, None, None)
	return (True, source, branch)


def install_autocomplete():
	err("Autocomplete auto-installer is currently disabled. ")
	err("Please install it manually from https://github.com/kislyuk/argcomplete.git")
	return False
	# TODO: Fix me
	#root = util.lmh_root()+"/ext"
	#util.git_clone(root, "https://github.com/kislyuk/argcomplete.git", "arginstall")
	#call([python, "setup.py", "install", "--user"], cwd=root+"/arginstall")
	#activatecmd = root+"/arginstall/scripts/activate-global-python-argcomplete";
	#print "running %r"%(activatecmd)
	#call([root+"/arginstall/scripts/activate-global-python-argcomplete"])

#
# Main Setup Routines
#

def run_setup(args):
	"""Perform various setup functions"""

	# Check dependencies first
	if (not args.force) and (not check_deps()):
		err("Dependency check failed, either install dependencies manually ")
		err("or use --force to ignore dependency checks. ")
		return False


	action = args.m_action

	if action == "":
		# If there is nothing special to do, install everything
		if args.latexml_action == "" and args.stex_action == "" and args.mmt_action == "" and args.latexmls_action == "" and args.latexmlstomp_action == "":
			action = "in"
		else:
			action = "sk"

	# LaTeXML: git, cpanm
	latexml_source = get_config("setup::latexml::source")
	latexml_branch = get_config("setup::latexml::branch")
	(success, latexml_source, latexml_branch) = git_run_setup("LaTeXML", args.latexml_action, True, args.latexml_source, ext_dir, action, latexml_source, latexml_branch)
	if not success:
		return False

	# LaTeXMLs: git, cpanm
	latexmls_source = get_config("setup::latexmls::source")
	latexmls_branch = get_config("setup::latexmls::branch")
	(success, latexmls_source, latexmls_branch) = git_run_setup("LaTeXMLs", args.latexmls_action, True, args.latexmls_source, ext_dir, action, latexmls_source, latexmls_branch)
	if not success:
		return False

	# LaTeXMLStomp: git, cpanm
	latexmlstomp_source = get_config("setup::latexmlstomp::source")
	latexmlstomp_branch = get_config("setup::latexmlstomp::branch")
	(success, latexmlstomp_source, latexmlstomp_branch) = git_run_setup("LaTeXMLStomp", args.latexmlstomp_action, True, args.latexmlstomp_source, ext_dir, action, latexmlstomp_source, latexmlstomp_branch)
	if not success:
		return False

	# sTeX: git, no cpanm
	stex_source = get_config("setup::stex::source")
	stex_branch = get_config("setup::stex::branch")
	(success, stex_source, stex_branch) = git_run_setup("sTeX", args.stex_action, False, args.stex_source, ext_dir, action, stex_source, stex_branch)
	if not success:
		return False

	# MMT: svn, no cpanm
	mmt_source = get_config("setup::mmt::source")
	mmt_branch = get_config("setup::mmt::branch")
	(success, mmt_source, mmt_branch) = svn_run_setup("MMT", args.mmt_action, False, args.mmt_source, ext_dir, action, mmt_source, mmt_branch)
	if not success:
		return False

	# Store all the selcted sources back in the config.
	if args.store_source_selections:
		set_config("setup::latexml::source", latexml_source)
		set_config("setup::latexml::branch", latexml_branch)

		set_config("setup::latexmls::source", latexmls_source)
		set_config("setup::latexmls::branch", latexmls_branch)

		set_config("setup::latexmlstomp::source", latexmls_source)
		set_config("setup::latexmlstomp::branch", latexmls_branch)

		set_config("setup::stex::source", stex_source)
		set_config("setup::stex::branch", stex_branch)

		set_config("setup::mmt::source", mmt_source)
		set_config("setup::mmt::branch", mmt_branch)

	if args.autocomplete:
		std("Installing autocomplete ...")
		install_autocomplete()

	if args.add_private_token and len(args.add_private_token) == 1:
		std("Adding private token ...")
		set_config("gl::private_token", args.add_private_token[0])

	return True

def get_template(name):
    return read_file(install_dir + "/bin/templates/" + name)
