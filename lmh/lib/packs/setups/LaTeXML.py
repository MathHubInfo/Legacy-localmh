from lmh.lib.packs import classes
from lmh.lib.config import get_config

latexml_source = get_config("setup::latexml::source")
latexml_branch = get_config("setup::latexml::branch")

setup = classes.GitPack("LaTeXML", latexml_source, latexml_branch, cpanm=True)
