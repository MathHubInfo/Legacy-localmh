from lmh.lib.packs import classes
from lmh.lib.config import get_config

latexmlstex_source = get_config("setup::latexmlstex::source")
latexmlstex_branch = get_config("setup::latexmlstex::branch")

setup = classes.GitPack("LaTeXMLsTeX", latexmlstex_source, latexmlstex_branch, cpanm=True)
