from lmh.lib.packs import classes
from lmh.lib.config import get_config

latexmlkwarc_source = get_config("setup::latexmlkwarc::source")
latexmlkwarc_branch = get_config("setup::latexmlkwarc::branch")

setup = classes.GitPack("LaTexMLKWARC", latexmlkwarc_source, latexmlkwarc_branch, cpanm=True)
