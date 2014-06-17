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

repo_wildcard_local = """
Repository names allow using globs to match repositories and relative paths.

Examples:
    *         - would match all repositories from all groups.
    mygroup/* - would match all repositories from group mygroup
    .         - would run on local directory

Note that common linux shells (such as bash) automatically resolve globs in the
local directory. To avoid this, you can use single quotation marks.
"""

repo_wildcard_remote = """
Repository names allow using globs to match repositories.

Examples:
    *         - would match all repositories from all groups.
    mygroup/* - would match all repositories from group mygroup

Note that common linux shells (such as bash) automatically resolve globs in the
local directory. To avoid this, you can use single quotation marks.
"""
