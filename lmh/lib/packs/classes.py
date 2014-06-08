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
import shutil
import os.path
from subprocess import call

from lmh.lib.io import std, err, read_file
from lmh.lib.env import install_dir, ext_dir
from lmh.lib.extenv import perl5env, perl5root, cpanm_executable, perl_executable, make_executable
from lmh.lib.config import get_config, set_config
from lmh.lib.git import pull as git_pull
from lmh.lib.git import clone as git_clone
from lmh.lib.svn import pull as svn_pull
from lmh.lib.svn import clone as svn_clone

class UnsupportedAction(Exception):
    """Thrown if a setup action is not supported. """
    pass

class Pack():
    """A normal Pack"""
    def __init__(self, name):
        self.name = name
        pass
    def post_change_hook(self, pack_dir):
        """Hook that is called after changes take place. """
        return True
    def do_install(self, pack_dir, params):
        """Performs the installation of this pack. """
        raise UnsupportedAction
    def install(self, pack_dir, params = ""):
        """Installs this packs. """
        if not self.do_install(pack_dir, params):
            return False
        return self.post_change_hook(pack_dir)
    def do_update(self, pack_dir, params):
        """Performs the update of this pack. """
        raise UnsupportedAction
    def update(self, pack_dir, params = ""):
        """Updates this pack."""
        if not self.do_update(pack_dir, params):
            return False
        return self.post_change_hook(pack_dir)
    def do_remove(self, pack_dir, params):
        """Performs the removal of the pack. """
        try:
            shutil.rmtree(pack_dir)
            return True
        except:
            return False
    def remove(self, pack_dir, params = ""):
        """Removes this pack"""
        return self.do_remove(pack_dir, params)
    def is_installed(self, pack_dir, params = ""):
        return os.path.isdir(pack_dir)

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

#
# CPANM
#

# Is cpanm selfcontained? Check the config setting
if get_config("setup::cpanm::selfcontained"):
    cpanm_installdeps_args = [cpanm_executable, "-L", perl5root[0], "--installdeps", "--prompt", "."]
    cpanm_installself_args = [cpanm_executable, "-L", perl5root[0], "--notest", "--prompt", "."]
else:
    cpanm_installdeps_args = [cpanm_executable, "--installdeps", "--prompt", "."]
    cpanm_installself_args = [cpanm_executable, "--notest", "--prompt", "."]

def cpanm_make(pack_dir):
    """Run CPANM make commands for a package. """

    _env = perl5env(os.environ)
    _env.pop("STEXSTYDIR", None)

    try:
        call(cpanm_installdeps_args, env=_env, cwd=pack_dir, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
        call(cpanm_installself_args, env=_env, cwd=pack_dir, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
        return True
    except Exception as e:
        err("Failed to run cpanm on", pack_dir)
        return False

class GitPack(Pack):
    """A Pack that is managed by git"""
    def __init__(self, name, def_source, def_branch, cpanm=False):
        self.name = name
        self.dsource = def_source
        self.dbranch = def_branch
        self.cpanm = cpanm
    def do_install(self, pack_dir, sstring):
        """Installs a git controlled package. """
        (source, branch) = get_item_source(sstring, self.dsource, self.dbranch, self.name)

        try:
            if branch == "":
                return git_clone(ext_dir, source, pack_dir)
            else:
                return git_clone(ext_dir, source, "-b", branch, pack_dir)
        except:
            err("git clone failed to clone", source, ". Check your network connection. ")
            return False
    def do_update(self, pack_dir, sstring):
        """Updates a git controlled package. """
        try:
            return git_pull(pack_dir)
        except:
            err("git pull failed to update. Check your network connection. ")
            return False
    def post_change_hook(self, pack_dir):
        if self.cpanm:
            std("Running cpanm on", pack_dir)
            return cpanm_make(pack_dir)
        else:
            return True

class SVNPack(Pack):
    """A Pack that is managed by svn"""
    def __init__(self, name, def_source, def_branch, cpanm=False):
        self.name = name
        self.dsource = def_source
        self.dbranch = def_branch
        self.cpanm = cpanm
    def do_install(self, pack_dir, sstring):
        """Installs a svn controlled package. """
        (source, branch) = get_item_source(sstring, self.dsource, self.dbranch, self.name)

        try:
            if branch == "":
                return svn_clone(ext_dir, source, pack_dir)
            else:
                return svn_clone(ext_dir, source, "-b", branch, pack_dir)
        except:
            err("svn checkout failed to checkout", source, ". Check your network connection. ")
            return False
    def do_update(self, pack_dir, sstring):
        """Updates a svn controlled package. """
        try:
            return svn_pull(pack_dir)
        except:
            err("svn update failed to update. Check your network connection. ")
            return False
    def post_change_hook(self, pack_dir):
        if self.cpanm:
            std("Running cpanm on", pack_dir)
            return cpanm_make(pack_dir)
        else:
            return True