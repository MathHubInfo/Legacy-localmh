from lmh.lib.packs import classes

from lmh.lib.dirs import lmh_locate
from lmh.lib.env import wget_executable
from lmh.lib.utils import mkdir_p
from lmh.lib.config import get_config

import subprocess
import os.path
import os
import stat
import sys

mmt_jar_dir = lmh_locate("ext", "MMT", "deploy")
mmt_jar_path = lmh_locate(mmt_jar_dir, "mmt.jar")


class MMTPack(classes.Pack):
    """The special MMT Pack"""
    def __init__(self, mmt_jar_source):
        self.mmt_jar_source = mmt_jar_source
        self.name = "MMT"
    def do_install(self, pack_dir, sstring):
        """Updates the MMT package"""
        return self.do_update(pack_dir,sstring)
    def do_update(self, pack_dir, sstring):
        """Install the MMT package"""

        # Make the directory
        mkdir_p(mmt_jar_dir)
        
        # and wget it, overwriting the existing jar
        proc = subprocess.Popen([wget_executable, self.mmt_jar_source, "-O", mmt_jar_path], stderr=sys.stderr, stdout=sys.stdout)
        proc.wait()

        # chmod +x mmt_jar_path
        st = os.stat(mmt_jar_path)
        os.chmod(mmt_jar_path, st.st_mode | stat.S_IEXEC)

        return proc.returncode == 0

setup = MMTPack(get_config("setup::mmtjar::source"))
