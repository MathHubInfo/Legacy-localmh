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

import json
import os.path

from lmh.lib.io import std, err, read_file
from lmh.lib.env import install_dir, ext_dir
from lmh.lib.packs import classes


#
# Package Lookers
#

"""All available packs"""
av_packs = json.loads(read_file(install_dir + "/lmh/data/packs.json"))

# Generate the all group, which is everything except for self.
av_packs["groups"]["all"] = list(av_packs["packs"].keys())
av_packs["groups"]["all"].remove("self")

#
# Resolve the specification for a certain pack
#

def resolve_package_spec(packages):
    """Resolves package specification. """

    to_install = set()
    for p in packages:
        (pname, sep, pconfig) = p.partition(":")
        if pname in av_packs["packs"]:
            to_install.add(p)
        elif pname in av_packs["groups"]:
            for q in av_packs["groups"][p]:
                to_install.add(q+sep+pconfig)
        else:
            err("No package or group with the name", pname, "found. ")
    return sorted(to_install, key=lambda p:av_packs["packs"][p.partition(":")[0]])


#
# General Pack Setup things
#

def import_pack(pack):
    # Imports a pack installer from a file
    pimport = __import__("lmh.lib.packs.setups."+pack)
    pimport = getattr(pimport, "lib")
    pimport = getattr(pimport, "packs")
    pimport = getattr(pimport, "setups")
    pimport = getattr(pimport, pack)
    return pimport

def get_pack_setup(pack):
    try:
        return import_pack(pack).setup
    except ImportError:
        err("Unable to load pack setup for pack", pack)
        err("Please check that the pack exists. ")
        return False
    except AttibuteError:
        err("Unable to load pack setup for pack", pack)
        err("Please check that the pack exists. ")
        return False

def get_pack_dir(pack):
    return os.path.join(ext_dir, pack)

#
# Installing packs
#

def install_pack(pack):
    """Installs a single pack"""

    (pack, sep, pconfig) = pack.partition(":")

    pack_setup = get_pack_setup(pack)
    pack_dir = get_pack_dir(pack)

    if not pack_setup:
        return False

    if pack_setup.is_installed(pack_dir):
        err("Pack", pack, "is already installed, use --update to update. ")
        return False

    try:
        return pack_setup.install(pack_dir, pconfig)
    except classes.UnsupportedAction:
        err("Pack", pack, "does not support installing. You may want to --update the pack?")
        return False

def install(*packs):
    """Installs a number of packs. """

    ret = True
    packs = resolve_package_spec(packs)

    for pack in packs:
        ret = install_pack(pack) or ret
    return ret

#
# Updating packs
#


def update_pack(pack):
    """Updates a single pack. """

    (pack, sep, pconfig) = pack.partition(":")

    pack_setup = get_pack_setup(pack)
    pack_dir = get_pack_dir(pack)

    if not pack_setup:
        return False

    if not pack_setup.is_installed(pack_dir):
        err("Pack", pack, "is not installed, can not update. ")
        return False

    try:
        return pack_setup.update(pack_dir, pconfig)
    except classes.UnsupportedAction:
        err("Pack", pack, "does not support updating. You may want to --reset the pack. ")
        return False


def update(*packs):
    """Updates a number of packs. """

    ret = True
    packs = resolve_package_spec(packs)

    for pack in packs:
        ret = update_pack(pack) or ret
    return ret

#
# Removing packs
#

def remove_pack(pack):
    """Removes a single pack. """

    (pack, sep, pconfig) = pack.partition(":")

    pack_setup = get_pack_setup(pack)
    pack_dir = get_pack_dir(pack)

    if not pack_setup:
        return False

    if not pack_setup.is_installed(pack_dir):
        err("Pack", pack, "is not installed, can not remove. ")
        return False

    try:
        return pack_setup.remove(pack_dir, pconfig)
    except classes.UnsupportedAction:
        err("Pack", pack, "does not support removal. Maybe you can remove it manually. ")
        return False


def remove(*packs):
    """Removes a number of packs. """

    ret = True
    packs = resolve_package_spec(packs)

    for pack in packs:
        ret = remove_pack(pack) or ret
    return ret

#
# Reseting packs
#

def reset_pack(pack):
    """Resets a single pack. """

    (pack, sep, pconfig) = pack.partition(":")

    pack_setup = get_pack_setup(pack)
    pack_dir = get_pack_dir(pack)

    if not pack_setup:
        return False

    if not pack_setup.is_installed(pack_dir):
        err("Pack", pack, "is not installed, skipping removal. ")
    else:
        if not remove_pack(pack+sep+pconfig):
            err("Pack", pack, "could not be removed, --reset has failed. ")
            return False

    if not install_pack(pack+sep+pconfig):
        err("Pack", pack, "could not be (re)installed, --reset has failed. ")
        return False
    return True


def reset(*packs):
    """Resets a number of packs. """

    ret = True
    packs = resolve_package_spec(packs)

    for pack in packs:
        ret = reset_pack(pack) or ret
    return ret
