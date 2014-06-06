"""
This file is part of LMH.

LMH is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

LMH is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with LMH.  If not, see <http://www.gnu.org/licenses/>.
"""
from lmh.lib.packs import classes
from lmh.lib.config import get_config

latexml_source = get_config("setup::latexml::source")
latexml_branch = get_config("setup::latexml::branch")

setup = classes.GitPack("LaTeXML", latexml_source, latexml_branch, cpanm=True)
