import os.path
import os
import re
from lmh.lib.io import std, err, read_file, write_file
from lmh.lib.repos.local.package import get_metainf_lines
from lmh.lib.repos.local import match_repo
from lmh.lib.git import do, do_data, make_orphan_branch
from lmh.lib.config import get_config

# Config setting for generated branches.
gbranchstring = "generated-branches:"

class Generated:
    def __init__(self, rep):
        """
            Loads information about generated repositories.
        """

        # Get the repository.
        self.repo = match_repo(rep)

        # Check if we exist at all.
        if not self.repo:
            err("Unable to find repository '"+rep+"'")

        # Initialise the cache.
        self.__branch_cache = None

    #
    # GENERIC STATUS FUNCTIONS
    #

    def get_all_branches(self, tuple = True):
        """
            Gets names and paths for all the genereted branches.
        """

        if self.__branch_cache:
            if tuple:
                return self.__branch_cache
            else:
                return [b[0] for b in self.__branch_cache]

        # Helper function to split branch specififcation into
        # branch and folder name.

        def split_branch(bstr):
            bsplit = bstr.split(":")
            if len(bsplit) == 1:
                return (bsplit[0], bsplit[0])
            else:
                return (bsplit[0], bsplit[1])


        # Names for the branches.
        branchnames = []

        # get the meta-inf lines.
        for l in get_metainf_lines(self.repo):
            if l.startswith(gbranchstring):
                # and find all the branch stuffs.
                l = re.sub("\s+", " ", l[len(gbranchstring):]).strip()
                branchnames.extend(l.split(" "))

        # write the splits into the cache
        self.__branch_cache = map(split_branch, branchnames)

        # and return that.
        if tuple:
            return self.__branch_cache
        else:
            return [b[0] for b in self.__branch_cache]

    def clear_branch_cache(self):
        """
            Clears the cache of all generated branches.
        """
        self.__branch_cache = None

    def get_branch_path(self, branch, tuple = False):
        """
            Gets the path to a given branch.
        """

        for b in self.get_all_branches():
            if b[0] == branch:
                return b if tuple else b[1]

        return None
    def get_paths(self, branch):
        rpath = match_repo(self.repo, abs=True)

        if not self.get_branch_path(branch):
            return (rpath, False)

        dpath = os.path.join(rpath, self.get_branch_path(branch))

        return (rpath, dpath)

    def is_installed(self, branch):
        """
            Checks if a specific branch is installed.
        """

        # Resolve path to branch.
        (rpath, dpath) = self.get_paths(branch)

        if not dpath:
            err("Unable to find given generated content branch. ")
            return False

        return os.path.isdir(dpath)

    #
    # HIGHER LEVEL FUNCTIONS
    #

    def print_status(self):
        """
            Prints some status information about the branches.
        """
        std(    "Repository Name:    ", self.repo)

        for (b, p) in self.get_all_branches():
            std("Generated Branch:   ", "'"+b+"'")
            std("Path:               ", "'"+p+"'")
            std("Installed:          ", "Yes" if self.is_installed(b) else "No")

    def init_branch(self, branch):
        """
            Creates a new branch for status information.
        """

        # Get name and path.
        bsplit = branch.split(":")
        if len(bsplit) == 1:
            (name, pth) = (bsplit[0], bsplit[0])
        else:
            (name, pth) = (bsplit[0], bsplit[1])

        std("Creating branch '"+name+"' at '"+pth+"'. ")

        # Check if the branch already exists.
        if name in self.get_all_branches(tuple=False):
            err("Branch '"+name+"' already exists, can not create it again. Use --install to install. ")
            return False

        # Get the paths
        rpath = match_repo(self.repo, abs=True)
        dpath = os.path.join(rpath, pth)
        meta_inf_path = os.path.join(rpath, "META-INF", "MANIFEST.MF")

        # Find paths for the .gitignore
        gitignore_path = os.path.join(rpath, ".gitignore")
        gitignore_entry = os.path.join("/", pth)+"\n"

        # and either add to it or create it.
        if os.path.isfile(gitignore_path):
            write_file(gitignore_path, read_file(gitignore_path)+gitignore_entry)
        else:
            write_file(gitignore_path, gitignore_entry)

        # Update the meta-inf
        written = False
        lines = get_metainf_lines(self.repo)

        # try to append it to a line that already exists.
        for (i, l) in enumerate(lines):
            if l.startswith(gbranchstring):
                lines[i] = lines[i].rstrip("\n") + " " + branch
                written = True
                break

        # or make a new one.
        if written == False:
            lines.extend([gbranchstring+" "+ branch])

        # and write that file.
        write_file(meta_inf_path, lines)

        # Create the orphaned branch.
        if not make_orphan_branch(rpath, name):
            return False

        # push it
        if not do(rpath, "push", "-u", "origin", name):
            err("Pushing branch to origin failed. ")
            return False

        # Clear the deploy branch cache for this repository.
        self.clear_branch_cache()

        # install it.
        if not self.install_branch(name):
            return False

        # change the commit message
        if not do(dpath, "commit", "--amend", "--allow-empty", "-m", "Create deploy branch. "):
            return False

        # and push it.
        if not do(dpath, "push", "--force", "origin", name):
            return False

        std("Generated files branch '"+name+"' created, installed and pushed. ")
        std("Please commit and push META-INF/MANIFEST.MF and .gitignore to publish installation. ")

        return True

    def install_branch(self, branch):
        """
            Installs the given branch.
        """

        # Resolve path to branch.
        (rpath, dpath) = self.get_paths(branch)

        # make sure it exists
        if not dpath:
            err("Unable to find given generated content branch '"+branch+"'. ")
            return False

        # and is not installed.
        if self.is_installed(branch):
            err("Given generated branch '"+branch+"' already installed. Did you want to pull?")
            return False

        (o, e) = do_data(rpath, "config", "--local", "--get", "remote.origin.url")

        if not do(rpath, "rev-parse", "--verify", "--quiet", branch):
            if not do(rpath, "branch", branch, "--track", "origin/"+branch):
                return False

        # Clone it shared
        if not do(rpath, "clone", rpath, dpath, "--shared", "-b", branch):
            return False

        # set up .git/objects/info/alternates relatively
        if not write_file(os.path.join(dpath, ".git/objects/info/alternates"), "../../../.git/objects"):
            return False

        # and set the origin correctly.
        if not do(dpath, "remote", "set-url", "origin", o.rstrip("\n")):
            return False

        return do(rpath, "branch", "-D", branch)


    def pull_branch(self, branch):
        """
            Pulls the given branch.
        """

        # Resolve path to branch.
        (rpath, dpath) = self.get_paths(branch)

        # make sure it exists
        if not dpath:
            err("Unable to find given generated content branch '"+branch+"'. ")
            return False

        # make sure it exists
        if not dpath:
            err("Unable to find given generated content branch '"+branch+"'. ")
            return False

        # and is installed.
        if not self.is_installed(branch):
            err("Given generated branch '"+branch+"' is not installed, can not pull. ")
            return False

        # Fetch origin in the clone repo.
        if not do(rpath, "fetch", "--depth", "1", "origin", branch):
            return False

        # Hard reset this repository.
        if not do(dpath, "reset", "--hard", "origin/"+branch):
            return False

        # Run some housekeeping in the parent repo
        return do(rpath, "gc", "--auto")


    def push_branch(self, branch):
        """
            Pushes the given branch.
        """

        # Resolve path to branch.
        (rpath, dpath) = self.get_paths(branch)

        # make sure it exists
        if not dpath:
            err("Unable to find given generated content branch '"+branch+"'. ")
            return False

        # and is installed.
        if not self.is_installed(branch):
            err("Given generated branch '"+branch+"' is not installed, can not push. ")
            return False

        # add all the changes.
        if not do(dpath, "add", "-A", "."):
            return False

        # commit them.
        if not do(dpath, "commit", "--amend", "--allow-empty", "-m", "Update generated content"):
            return False

        # and force push them.
        if not do(dpath, "push", "--force", "origin", branch):
            return False

        # and thats it.
        return True
