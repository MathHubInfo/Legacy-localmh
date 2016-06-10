# LocalMH

LocalMH is an infrastructure for local (in a working tree) management of the content in http://mathhub.info.

## Install

Currently, the only supported way to install localmh is to use [localmh_docker](https://github.com/KWARC/localmh_docker).
You need Python 3.5+ in order to run this tool.

## Documentation

Basic Instructions on how to use lmh can be found at [http://mathhub.info/help/offline-authoring](http://mathhub.info/help/offline-authoring).

New documentation (still in development) can be found under docs/. It can be generated with [MkDocs](http://www.mkdocs.org/).

## Directory Structure

LMH is split up into serveral directories:
* Source Directories: Used for source code and other core files.
  * bin:      contains template and main script
  * lmh:			main source directory for lmh
  * docs:			Documentation (work in progess)
  * sty:      LaTeX packages used in MathHub.info
  * styles:		for the notation definitions MMT uses for generating XHTML from OMDoc
* Data Directories: Used for user-generated content and other Data
  * MathHub:  stored offline content from MathHub.info
  * ext:      external Software (that is installed automatically)
  * logs:			crash reports that will help developers improve lmh.

## License

GPL, version 3.0

For the full license text, please see [gpl-3.0.txt](gpl-3.0.txt).
