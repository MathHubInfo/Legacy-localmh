from lmh.lib.packs import classes
from lmh.lib.config import get_config

latexmls_source = get_config("setup::latexmls::source")
latexmls_branch = get_config("setup::latexmls::branch")

setup = classes.GitPack("LaTeXMLs", latexmls_source, latexmls_branch, cpanm=True)
