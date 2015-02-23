from lmh.lib.packs import classes
from lmh.lib.config import get_config

stex_source = get_config("setup::stex::source")
stex_branch = get_config("setup::stex::branch")

setup = classes.GitPack("sTeX", stex_source, stex_branch, cpanm=False)
