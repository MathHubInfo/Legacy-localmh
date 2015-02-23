
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
