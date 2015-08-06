import sys
import shutil
import os.path
from subprocess import call

from lmh.lib.io import std, err
from lmh.lib.env import ext_dir
from lmh.lib.extenv import perl5env, perl5root, cpanm_executable
from lmh.lib.config import get_config, set_config
from lmh.lib.git import pull as git_pull
from lmh.lib.git import clone as git_clone
from lmh.lib.git import do as git_do

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
    def is_managed(self):
        managed_packs = get_config("setup::unmanaged").split(",")
        return not (self.name in managed_packs)
    def mark_managed(self):
        # we are already managed.
        if self.is_managed():
            return True

        # else we need to be removed
        managed_packs = get_config("setup::unmanaged").split(",")
        while self.name in managed_packs:
            managed_packs.remove(self.name)

        # and store it.
        set_config("setup::unmanaged", ",".join(managed_packs))
        return True
    def mark_unmanaged(self):
        # we are already unmanaged.
        if not self.is_managed():
            return True

        # else we need to be added
        managed_packs = get_config("setup::unmanaged").split(",")
        managed_packs.append(self.name)

        # and store it.
        set_config("setup::unmanaged", ",".join(managed_packs))
        return True



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
    cpanm_installdeps_args = [cpanm_executable, "-L", perl5root[0], "--notest", "--installdeps", "--prompt", "."]
    cpanm_installself_args = [cpanm_executable, "-L", perl5root[0], "--notest", "--prompt", "."]
else:
    cpanm_installdeps_args = [cpanm_executable, "--notest", "--installdeps", "--prompt", "."]
    cpanm_installself_args = [cpanm_executable, "--notest", "--prompt", "."]
cpanm_selfupgrade_args = [cpanm_executable, "--self-upgrade"]


def cpanm_make(pack_dir):
    """Run CPANM make commands for a package. """

    _env = perl5env(os.environ)
    _env.pop("STEXSTYDIR", None)
    try:
        call(cpanm_selfupgrade_args)
        call(cpanm_installdeps_args, env=_env, cwd=pack_dir, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
        call(cpanm_installself_args, env=_env, cwd=pack_dir, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
        return True
    except Exception as e:
        err(e)
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
            # git clone first
            if not git_clone(ext_dir, source, pack_dir):
                return False

            # do the checkout
            if branch != "":
                return git_do(os.path.join(ext_dir, pack_dir), "checkout", branch)
            else:
                return True
        except:
            err("git clone failed to clone", source, ". Check your network connection. ")
            return False
    def do_update(self, pack_dir, sstring):
        """Updates a git controlled package. """
        try:
            return git_pull(pack_dir)
        except:
            err("git pull failed to update. Please make sure that you have a network connection. ")
            err("If you were using a specific version (with the PACKAGE:URL@REFSEPEC syntax), try using --reinstall. ")
            return False
    def post_change_hook(self, pack_dir):
        if self.cpanm:
            std("Running cpanm on", pack_dir)
            return cpanm_make(pack_dir)
        else:
            return True
