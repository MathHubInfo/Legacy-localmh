def about():
    return "Translate existing multilingual modules to a new language"

def add_parser_args(parser, argparse):
    parser.add_argument('--force', action="store_true", default=False, help="Overwrite existing modules. ")
    parser.add_argument('source', nargs=1, help="Name of the existing language. ")
    parser.add_argument('dest', nargs="+", help="Name(s) of the new language(s). ")
    parser.add_argument('--terms', default=None, help="Terms to pre-translate. Either a Path to a json file or a JSON-encoded string. ")

    parser.epilog = """
Example: lmh translate functions.en.tex de

Which translates the english version functions.en.tex to a new german version
which will be called functions.de.tex.

The terms argument should have the following structure:

{
"source_language": {
    "target_language": {
        "word": "translation"
    }
}
}

Will require manual completion of the translation. """
