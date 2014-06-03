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

import argparse

from lmh.lib.self import run_setup

def create_parser():
  parser = argparse.ArgumentParser(description='Local MathHub Setup tool.')
  add_parser_args(parser)
  return parser

def add_parser(subparsers, name="setup"):
  parser_status = subparsers.add_parser('setup', formatter_class=argparse.RawTextHelpFormatter, help='sets up local math hub and fetches external requirements')
  add_parser_args(parser_status)

def add_parser_args(parser):
  action = parser.add_argument_group('Setup actions').add_mutually_exclusive_group()
  action.add_argument('--install', action="store_const", dest="m_action", const="in", default="", help='Perform initial setup of dependencies. Default if no other arguments are given. ')
  action.add_argument('--update', action="store_const", dest="m_action", const="up", help='Update existing versions of dependencies. Implies --update-* arguments. ')
  action.add_argument('--reinstall', action="store_const", dest="m_action", const="re", help='Perform initial setup of dependencies. ')
  action.add_argument('--skip', action="store_const", dest="m_action", const="sk", help='Skip everything which is not specified explicitly. ')

  parser.add_argument('-f', '--force', action="store_const", dest="force", const=True, default=False, help='Skip checking for lmh core requirements. ')
  parser.add_argument('--autocomplete', default=False, const=True, action="store_const", help="should install autocomplete for bash", metavar="")
  parser.add_argument('--store-source-selections', default=False, const=True, action="store_const", help="If set all source and branch selections are stored and used as default in the future. ", metavar="")
  parser.add_argument('--add-private-token', nargs=1, help="add private token to use advanced MathHub functionality")
  

  source = parser.add_argument_group('Dependency versions')
  source.add_argument('--latexml-source', default="", metavar="source@branch", help='Get LaTeXML from the given source. ')
  source.add_argument('--latexmls-source', default="", metavar="source@branch", help='Get LaTeXMLs from the given source. ')
  source.add_argument('--latexmlstomp-source', default="", metavar="source@branch", help='Get LaTeXMLStomp from the given source. ')
  source.add_argument('--stex-source', default="", metavar="source@branch", help='Get sTex from the given source. ')
  source.add_argument('--mmt-source', default="", metavar="source@branch", help='Get MMT from the given source. ')

  latexml = parser.add_argument_group('LaTeXML').add_mutually_exclusive_group()
  latexml.add_argument('--install-latexml', action="store_const", dest="latexml_action", const="in", default="", help='Install LaTexML. ')
  latexml.add_argument('--update-latexml', action="store_const", dest="latexml_action", const="up", help='Update LaTeXML. ')
  latexml.add_argument('--reinstall-latexml', action="store_const", dest="latexml_action", const="re", help='Reinstall LaTeXML. ')
  latexml.add_argument('--skip-latexml', action="store_const", dest="latexml_action", const="sk", help='Leave LaTeXML untouched. ')

  latexmls = parser.add_argument_group('LaTeXML::Plugin::latexmls').add_mutually_exclusive_group()
  latexmls.add_argument('--install-latexmls', action="store_const", dest="latexmls_action", const="in", default="", help='Install LaTexMLs. ')
  latexmls.add_argument('--update-latexmls', action="store_const", dest="latexmls_action", const="up", help='Update LaTeXMLs. ')
  latexmls.add_argument('--reinstall-latexmls', action="store_const", dest="latexmls_action", const="re", help='Reinstall LaTeXMLs. ')
  latexmls.add_argument('--skip-latexmls', action="store_const", dest="latexmls_action", const="sk", help='Leave LaTeXMLs untouched. ')

  latexmlstomp = parser.add_argument_group('LaTeXMLStomp').add_mutually_exclusive_group()
  latexmlstomp.add_argument('--install-latexmlstomp', action="store_const", dest="latexmlstomp_action", const="in", default="", help='Install LaTexMLStomp. ')
  latexmlstomp.add_argument('--update-latexmlstomp', action="store_const", dest="latexmlstomp_action", const="up", help='Update LaTeXMLStomp. ')
  latexmlstomp.add_argument('--reinstall-latexmlstomp', action="store_const", dest="latexmlstomp_action", const="re", help='Reinstall LaTeXMLStomp. ')
  latexmlstomp.add_argument('--skip-latexmlstomp', action="store_const", dest="latexmlstomp_action", const="sk", help='Leave LaTeXMLStomp untouched. ')

  stex = parser.add_argument_group('sTeX').add_mutually_exclusive_group()
  stex.add_argument('--install-stex', action="store_const", dest="stex_action", const="in", default="", help='Install sTeX. ')
  stex.add_argument('--update-stex', action="store_const", dest="stex_action", const="up", help='Update sTeX. ')
  stex.add_argument('--reinstall-stex', action="store_const", dest="stex_action", const="re", help='Reinstall sTeX. ')
  stex.add_argument('--skip-stex', action="store_const", dest="stex_action", const="sk", help='Leave sTeX untouched. ')

  mmt = parser.add_argument_group('MMT').add_mutually_exclusive_group()
  mmt.add_argument('--install-mmt', action="store_const", dest="mmt_action", const="in", default="", help='Install MMT. ')
  mmt.add_argument('--update-mmt', action="store_const", dest="mmt_action", const="up", help='Update MMT. ')
  mmt.add_argument('--reinstall-mmt', action="store_const", dest="mmt_action", const="re", help='Reinstall MMT. ')
  mmt.add_argument('--skip-mmt', action="store_const", dest="mmt_action", const="sk", help='Leave MMT untouched. ')



  parser.epilog = """
    lmh setup --- sets up additional software it requires to run correctly  

    To install and compile latexml you may need additional packages. On Ubuntu the package libgdbm-dev should be enough. 
  """

def do(args):
  return run_setup(args)