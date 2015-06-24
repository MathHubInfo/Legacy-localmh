def about():
    return "Setup local math hub and fetches external requirements"

def add_parser_args(parser, argparse):
    action = parser.add_argument_group('Setup actions').add_mutually_exclusive_group()

    action.add_argument('--install', action="store_const", dest="saction", const="install", default="", help="Installs a package or group. ")
    action.add_argument('--update', action="store_const", dest="saction", const="update", help="Updates a package or group. ")
    action.add_argument('--reset', '--reinstall', action="store_const", dest="saction", const="reset", help="Resets a package or group. ")
    action.add_argument('--remove', action="store_const", dest="saction", const="remove", help="Removes a package or group. ")

    parser.add_argument('--no-check', '--force', action="store_true", help="Do not check for external dependencies. ")
    parser.add_argument('pack', nargs="*", metavar="PACK:SOURCE")

    parser.epilog = """
lmh setup --- Manages extra software required or useful for work with lmh.

Packages are specefied in the format:

PACKAGE_NAME[:SOURCE]

Packages can be installed, updated, removed and reset (reinstalled) via
--install, --update and --reset respectively.

Some packages are installed via git or svn. For those the optional argument
SOURCE specefies which source repository should be used. These can be given in
the format URL[@REFSPEC]. A REFSPEC is either a version number (commit SHA for
git), a tag name or a branch name.
An example for this is:

lmh setup --install LaTeXML:@dev

which will install the dev branch of LaTeXML.

The following packages are available:

"LaTeXML"        LaTeXML
"LaTeXMLs"       LaTeXML PLugin latexmls
"LaTeXMLStomp"   LaTeXML Plugin latexmlstomp
"sTeX"           sTeX
"MMT"            MMT
"self"           Meta Package which only supports the update option. Can be used
               to update lmh.

There are also package groups which simply install several packages at once.
Furthermore, if no packages are given, the "default" package group is used.

The following package groups are available:

"all"            Contains all packages except for the self package.
"default"        Contains LaTeXML, LaTeXMLs, sTeX and MMT.
"LaTeXML-all"    Installs LaTeXML and plugins.
"""
