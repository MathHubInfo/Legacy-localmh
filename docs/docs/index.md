# Localmh

Welcome to the documentation of localmh.

Lmh, short for <b>l</b>ocal <b>m</b>ath<b>h</b>ub, is an infrastructure for local (in a working tree) management of the content in [http://MathHub.info](http://MathHub.info).

As such it is mainly responsible for 2 different tasks:

* Mathhub Repositories installation and management
* External dependency management

It is still partially responsible for:

* Generation content creation (to be taken over MMT)

Lmh is licensed under GPL v3, see [License](license) for details.

## Installation

Installation should be done via [localmh_docker](https://github.com/KWARC/localmh_docker).

In case a manual installation is needed, instructions can be found [here](installation).

## Commands

### Repository management
* [lmh install](commands/install) - Installs Repositories
* [lmh ls-remote](commands/ls-remote) - Lists available repositories.

### (External) dependencies and software updates

* [lmh setup](commands/setup) - Sets up lmh and fetches external requirements
* [lmh selfupdate](commands/selfupdate) - Update lmh itself.

### Generation process

### Miscellaneous commands

* [lmh config](commands/config) - Configuration of localmh
* [lmh about](commands/about) - Shows version and general information
