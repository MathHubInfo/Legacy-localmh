from lmh.lib.packs import classes
from lmh.lib.config import get_config

mmt_source = get_config("setup::mmt::source")
mmt_branch = get_config("setup::mmt::branch")

setup = classes.SVNPack("MMT", mmt_source, mmt_branch, cpanm=False)
