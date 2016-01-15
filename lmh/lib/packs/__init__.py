import json
import os
import os.path

from lmh.lib.io import std, err, read_file
from lmh.lib.dirs import install_dir, ext_dir
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
    return import_pack(pack).setup

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

    # Create ext/ if it does not exist. 
    if not os.path.isdir(ext_dir):
        os.mkdir(ext_dir)

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

    if not pack_setup.is_managed():
        std("Pack", pack, "is marked as unmanaged, skipping update. ")
        return True

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
        err("Pack", pack, "is not installed, nothing to remove. ")
        return True

    if not pack_setup.is_managed():
        std("Pack", pack, "is marked as unmanaged, skipping removal. ")
        return True

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

    if not pack_setup.is_managed():
        std("Pack", pack, "is marked as unmanaged, skipping reset. ")
        return True

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

#
# Manage packs
#

def manage_pack(pack):
    """Marks a single pack as managed"""

    (pack, sep, pconfig) = pack.partition(":")

    std("Marked packaged '"+pack+"' as managed. ")

    return get_pack_setup(pack).mark_managed()

def manage(*packs):
    """Marks packs as managed. """

    ret = True
    packs = resolve_package_spec(packs)

    for pack in packs:
        ret = manage_pack(pack) or ret
    return ret

#
# Unmanage packs
#

def unmanage_pack(pack):
    """Marks a single pack as managed"""

    (pack, sep, pconfig) = pack.partition(":")

    std("Marked packaged '"+pack+"' as unamanged. ")

    return get_pack_setup(pack).mark_unmanaged()

def unmanage(*packs):
    """Marks packs as unmanaged. """

    ret = True
    packs = resolve_package_spec(packs)

    for pack in packs:
        ret = unmanage_pack(pack) or ret
    return ret

#
# Status of packs
#

def status_pack(pack):
    """Prints status of a pack"""

    (pack, sep, pconfig) = pack.partition(":")

    setup_pack = get_pack_setup(pack)
    pack_dir = get_pack_dir(pack)

    std("---")
    std("Package", pack)
    std("Installed:", setup_pack.is_installed(pack_dir))
    std("Managed:", setup_pack.is_managed())
    std("---")

    return True

def status(*packs):
    """Prints status of a pack. """

    ret = True
    packs = resolve_package_spec(packs)

    for pack in packs:
        ret = status_pack(pack) or ret
    return ret
