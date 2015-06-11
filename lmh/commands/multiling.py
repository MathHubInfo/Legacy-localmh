import os

from lmh.lib.io import err
from lmh.lib.modules.translate import create_multi

from . import CommandClass

class Command(CommandClass):
    def __init__(self):
        self.help="Create a new multilingual module from a monlingual one"
    def add_parser_args(self, parser):
        parser.add_argument('source', nargs=1, help="Name of the existing module. ")
        parser.add_argument('dest', nargs="+", help="Name(s) of the new language(s). ")
        parser.add_argument('--terms', default=None, help="Terms to pre-translate. Either a Path to a json file or a JSON-encoded string. ")

        parser.epilog = """
Example: lmh multiling mono.tex en de

Which creates a new multilingual module mono.tex with languages
mono.en.tex and mono.de.tex

The terms argument should have the following structure:

{
    "source_language": {
        "target_language": {
            "word": "translation"
        }
    }
}


Will require manual completion of the translations. """

    def do(self, args, unknown):
        args.source = args.source[0]

        if not os.path.isfile(args.source) or not args.source.endswith(".tex"):
            err("Module", args.source, "does not exist or is not a valid module. ")

        # Remove the .tex
        args.source = args.source[:-len(".tex")]

        return create_multi(args.source, args.terms, *args.dest)
