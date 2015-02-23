from . import CommandClass
from lmh.lib.repos.local import match_repo_args, clean
from lmh.lib.help import repo_wildcard_local

class Command(CommandClass):
    def __init__(self):
        self.help="Clean repositories of generated files"
    def add_parser_args(self, parser):
        ps = parser.add_mutually_exclusive_group()
        ps.add_argument('repository', nargs='*', default=[], help="A list of paths or repositories to generate things in. ")
        ps.add_argument('--all', "-a", default=False, const=True, action="store_const", help="generates files for all repositories")

        parser.add_argument('--git-clean', '-g', action="store_true", default=False, help="Also run git clean over all the repositories. ")

        parser.epilog = repo_wildcard_local

    def do(self, args, unparsed):
        repos = match_repo_args(args.repository, args.all)
        res = True
        for repo in repos:
            res = clean(repo, git_clean = args.git_clean) and res
        return res
