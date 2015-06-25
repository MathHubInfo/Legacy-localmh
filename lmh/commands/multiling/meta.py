def about():
    return "Create a new multilingual module from a monlingual one"

def add_parser_args(parser, argparse):
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
