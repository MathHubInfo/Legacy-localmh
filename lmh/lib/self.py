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
	
	# set the first run flag to false
	set_config("self::firstrun", False)

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

#
# latexml
#

def latexml_install(root, source, branch):
	"""Install latexml"""

	try:
		if branch == "":
			return git_clone(root, source, "LaTeXML")
		else:
			return git_clone(root, source, "-b", branch, "LaTeXML")
	except:
		err("Failed to install LaTeXML (is the source available? )")
		return False

def latexml_update(root, source, branch):
	"""Update latexml"""

	try:
		return git_pull(root + "/LaTeXML")
	except:
		err("Failed to update LaTeXML (is it present? )")
		return False


def latexml_remove(root, source, branch):
	"""Remove latexml"""
	try:
		shutil.rmtree(root + "/LaTeXML")
		return True
	except:
		err("Failed to remove LaTeXML (is it present? )")
		return False

# Arguments for installing via cpanm
if get_config("setup::cpanm::selfcontained"):
	cpanm_installdeps_args = [cpanm_executable, "-L", perl5root[0], "--installdeps", "--prompt", "."]
	cpanm_installself_args = [cpanm_executable, "-L", perl5root[0], "--notest", "--prompt", "."]
else:
	cpanm_installdeps_args = [cpanm_executable, "--installdeps", "--prompt", "."]
	cpanm_installself_args = [cpanm_executable, "--notest", "--prompt", "."]	


def latexml_make(root):
	"""Builds latexml"""

	_env = perl5env(os.environ)
	_env.pop("STEXSTYDIR", None)
	try:
		call(cpanm_installdeps_args, env=_env, cwd=root+"/LaTeXML", stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
		call(cpanm_installself_args, env=_env, cwd=root+"/LaTeXML", stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
		return True
	except Exception as e:
		err("Unable to run make commands for latexml. ")
		err(e)
		return False


#
# latexmls
#

def latexmls_install(root, source, branch):
	"""Install latexmls"""

	try:
		if branch == "":
			return git_clone(root, source, "LaTeXMLs")
		else:
			return git_clone(root, source, "-b", branch, "LaTeXMLs")
	except:
		err("Failed to install LaTeXMLs (is the source available? )")
		return False

def latexmls_update(root, source, branch):
	"""Update latexmls"""

	try:
		return git_pull(root + "/latexmls")
	except:
		err("Failed to update LaTeXMLs (is it present? )")
		return False


def latexmls_remove(root, source, branch):
	"""Remove latexmls"""

	try:
		shutil.rmtree(root + "/LaTeXMLs")
		return True
	except:
		err("Failed to remove LaTeXMLs (is it present? )")
		return False

def latexmls_make(root):
	"""Builds latexmls"""
	_env = perl5env(os.environ)
	_env.pop("STEXSTYDIR", None)
	try:
		call(cpanm_installdeps_args, env=_env, cwd=root+"/LaTeXMLs", stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
		call(cpanm_installself_args, env=_env, cwd=root+"/LaTeXMLs", stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
		return True
	except Exception as e:
		err("Unable to run make commands for latexmls. ")
		err(e)
		return False

#
# sTeX
#

def stex_install(root, source, branch):
	"""Install sTex"""

	try:
		if branch == "":
			return git_clone(root, source, "sTeX")
		else:
			return git_clone(root, source, "-b", branch, "sTeX")
	except:
		err("Failed to install sTex (is the source available? )")
		return False

def stex_update(root, source, branch):
	"""Update sTex"""

	try:
		return git_pull(root + "/sTeX")
	except:
		err("Failed to update sTex (is it present? )")
		return False


def stex_remove(root, source, branch):
	"""Remove sTex"""

	try:
		shutil.rmtree(root + "/sTeX")
		return True
	except:
		err("Failed to remove sTex (is it present? )")
		return False


#
# MMT
#

def mmt_install(root, source, branch):
	"""Install MMT"""

	try:
		if branch == "":
			return svn_clone(root, source, "MMT")
		else:
			return svn_clone(root, source + "@" + branch, "MMT")
	except Exception as e:
		err(e)
		err("Failed to install MMT (is it present? )")
		return False


def mmt_update(root, source, branch):
	"""Update MMT"""

	try:
		return svn_pull(root + "/MMT")
	except:
		err("Failed to update MMT (is it present? )")
		return False

def mmt_remove(root, source, branch):
	"""Remove MMT"""

	try:
		shutil.rmtree(root + "/MMT")
		return True
	except: 
		err("Failed to remove MMT (is it present? )")
		return False

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

def run_setup(args):
	"""Perform various setup functions"""

	if (not args.force) and (not check_deps()):
		err("Dependency check failed, either install dependencies manually ")
		err("or use --force to ignore dependency checks. ")
		return False

	action = args.m_action
	if action == "":
		if args.latexml_action == "" and args.stex_action == "" and args.mmt_action == "":
			action = "in"
		else:
			action = "sk"

	# LaTeXML
	latexml_action = args.latexml_action or action
	latexml_source = get_config("setup::latexml::source")
	latexml_branch = get_config("setup::latexml::branch")

	if not args.latexml_source == "":
		index = args.latexml_source.find("@")
		if index == 0:
			latexml_branch = args.latexml_source[1:]
		elif index > 0:
			latexml_source = args.latexml_source[:index]
			latexml_branch = args.latexml_source[index+1:]
		else:
			latexml_source = args.latexml_source

		std("Using LaTexML Version: "+latexml_source+"@"+latexml_branch)


	if latexml_action == "re":
		std("Reinstalling LaTexML ...")
		if not latexml_remove(ext_dir, latexml_source, latexml_branch):
			return False
		if not latexml_install(ext_dir, latexml_source, latexml_branch):
			return False
		if not latexml_make(ext_dir):
			return False
	if latexml_action == "in":
		std("Installing LaTeXML ...")
		if not latexml_install(ext_dir, latexml_source, latexml_branch):
			return False
		if not latexml_make(ext_dir):
			return False
	if latexml_action == "up":
		std("Updating LaTexML ...")
		if not latexml_update(ext_dir, latexml_source, latexml_branch):
			return False
		if not latexml_make(ext_dir):
			return False

	# LaTeXMLs
	latexmls_action = args.latexml_action or action
	latexmls_source = get_config("setup::latexmls::source")
	latexmls_branch = get_config("setup::latexmls::branch")

	if not args.latexmls_source == "":
		index = args.latexmls_source.find("@")
		if index == 0:
			latexmls_branch = args.latexmls_source[1:]
		elif index > 0:
			latexmls_source = args.latexmls_source[:index]
			latexmls_branch = args.latexmls_source[index+1:]
		else:
			latexmls_source = args.latexmls_source

		std("Using LaTeXMLs Version: "+latexmls_source+"@"+latexmls_branch)


	if latexmls_action == "re":
		std("Reinstalling LaTexMLs ...")
		if not latexmls_remove(ext_dir, latexmls_source, latexmls_branch):
			return False
		if not latexmls_install(ext_dir, latexmls_source, latexmls_branch):
			return False
		if not latexmls_make(ext_dir):
			return False
	if latexmls_action == "in":
		std("Installing LaTeXMLs ...")
		if not latexmls_install(ext_dir, latexmls_source, latexmls_branch):
			return False
		if not latexmls_make(ext_dir):
			return False
	if latexmls_action == "up":
		std("Updating LaTexMLs ...")
		if not latexmls_update(ext_dir, latexmls_source, latexmls_branch):
			return False
		if not latexmls_make(ext_dir):
			return False

	# sTex
	stex_action = args.stex_action or action
	stex_source = get_config("setup::stex::source")
	stex_branch = get_config("setup::stex::branch")

	if not args.stex_source == "":
		index = args.stex_source.find("@")
		if index == 0:
			stex_branch = args.stex_source[1:]
		elif index > 0:
			stex_source = args.stex_source[:index]
			stex_branch = args.stex_source[index+1:]
		else:
			stex_source = args.stex_source

		std("Using sTeX Version: "+stex_source+"@"+stex_branch)

	if stex_action == "re":
		std("Reinstalling sTeX ...")
		if not stex_remove(ext_dir, stex_source, stex_branch):
			return False
		if not stex_install(ext_dir, stex_source, stex_branch):
			return False
	if stex_action == "in":
		std("Installing sTex ...")
		if not stex_install(ext_dir, stex_source, stex_branch):
			return False
	if stex_action == "up":
		std("Updating sTex ...")
		if not stex_update(ext_dir, stex_source, stex_branch):
			return False

	# MMT
	mmt_action = args.mmt_action or action
	mmt_source = get_config("setup::mmt::source")
	mmt_branch = get_config("setup::mmt::branch")

	if not args.mmt_source == "":
		index = args.mmt_source.find("@")
		if index == 0:
			mmt_branch = args.mmt_source[1:]
		elif index > 0:
			mmt_source = args.mmt_source[:index]
			mmt_branch = args.mmt_source[index+1:]
		else:
			mmt_source = args.mmt_source

		std("Using MMT Version: "+mmt_source+"@"+mmt_branch)

	if mmt_action == "re":
		std("Reinstalling MMT ...")
		if not mmt_remove(ext_dir, mmt_source, mmt_branch):
			return False
		if not mmt_install(ext_dir, mmt_source, mmt_branch):
			return False
	if mmt_action == "in":
		std("Installing MMT ...")
		if not mmt_install(ext_dir, mmt_source, mmt_branch):
			return False
	if mmt_action == "up":
		std("Updating MMT ...")
		if not mmt_update(ext_dir, mmt_source, mmt_branch):
			return False

	if args.store_source_selections:
		# Store the selections in the config
		set_config("setup::latexml::source", latexml_source)
		set_config("setup::latexml::branch", latexml_branch)

		set_config("setup::latexmls::source", latexmls_source)
		set_config("setup::latexmls::branch", latexmls_branch)

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