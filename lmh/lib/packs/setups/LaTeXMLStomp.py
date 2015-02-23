from lmh.lib.packs import classes
from lmh.lib.config import get_config

latexmlstomp_source = get_config("setup::latexmlstomp::source")
latexmlstomp_branch = get_config("setup::latexmlstomp::branch")

setup = classes.GitPack("LaTeXMLStomp", latexmlstomp_source, latexmlstomp_branch, cpanm=True)
