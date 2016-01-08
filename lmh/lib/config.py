"""
Configuration functions for lmh
"""

# TODO: Prefer the file in the home directory. 
# If it does not exist, create it. 
# If it does exist, migrate automatically. 
# This will make sure that each user has their own configuration. 

import json

from lmh.lib.dirs import lmh_locate
from lmh.lib.io import std, err, read_file, write_file, term_colors

"""Available configuration values. """
config_meta = json.loads(read_file(lmh_locate("lib", "data", "config.json")))

"""The configuration file for lmh"""
config_file = lmh_locate("bin", "lmh.cfg") # TODO: Store this in the home direcory instead
                                            # will allow multiple users to read it. 

def get_config(key):
    """
    Gets a given configuration setting. If it does not exist in the 
    configuration file, the default will be returned
    """

    # check if the given key exists in the configuration
    if not key in config_meta:
        err("Option", key, "does not exist. ")
        raise KeyError

    # Read the setting from the config file
    # TODO: Think about verifying the type
    try:
        data = json.loads(read_file(config_file))

        return data[key]
    except:
        pass

    # return the default value
    return config_meta[key]["default"]

def format_type(t):
    """
    Formats a type for output to the command line
    """
    if t == "string":
        return term_colors("yellow")+"<string>"+term_colors("normal")
    elif t == "bool":
        return term_colors("green")+"<bool>"+term_colors("normal")
    elif t == "int":
        return term_colors("blue")+"<int>"+term_colors("normal")
    elif t == "int+":
        return term_colors("cyan")+"<int+>"+term_colors("normal")

def set_config(key, value):
    """
    Sets a configuration setting to a certain value. 
    """
    
    # first ensure the value is a string
    value = str(value)

    # check if the given key exists
    if not key in config_meta:
        err("Option", key, "does not exist. ")
        return False

    # Get the datatype of the config setting
    datatype = config_meta[key]["type"]
    
    # and typecast to the given type
    if datatype == "string":
        value = str(value)
    elif datatype == "bool":
        value = value.lower()
        if value == "true" or value == "1" or value == "on":
            value = True
        elif value == "false" or value == "0" or value == "off":
            value = False
        else:
            err("Option", key, " is of type boolean, please use the values 'true' or 'false'. ")
            return False
    elif datatype == "int":
        try:
            value = int(value)
        except:
            err("Option", key, " is of type integer, please use a valid integer. ")
            return False
    elif datatype == "int+":
        try:
            value = int(value)
            if value < 0:
                raise ValueError
        except:
            err("Option", key, " is of type positive integer, please use a valid positive integer. ")
            return False

    # Re-load the existing data
    data = {}
    try:
        data = json.loads(read_file(config_file))
    except:
        pass
    
    # write the config setting
    data[key] = value

    # and rew-rite the json file. 
    try:
        write_file(config_file, json.dumps(data, indent=4))
    except:
        err("Unable to write to config file. ")
        return False

    return True

def reset_config(key):
    """
    Resets a given config setting to the default by deleting it from the config
    file. 
    """

    # check if the given key exists
    if not key in config_meta:
        err("Option", key, " does not exist, unable to reset. ")
        return False
    
    # load the default and set it to that. 
    set_config(key, str(config_meta[key]["default"]))

def get_config_help(key):
    """
    Prints help to stdout about the given configuration settting. 
    """
    
    # check if the key exists
    if not key in config_meta:
        err("Option", key, " does not exist. ")
        return False

    # get its meta-information
    meta = config_meta[key]
    
    # and print that
    std(format_type(meta["type"]), key)
    std(meta["help"])
    std("Current Value: " + json.dumps(get_config(key)))
    std("Default Value: " + json.dumps(meta["default"]))

    return True

def list_config():
    """
    Prints information about all available configuration settings to stdout. 
    """

    for key in sorted(config_meta.keys()):
        try:
            if config_meta[key]["hidden"]:
                continue
        except:
            pass
        std(key +" =", format_type(config_meta[key]["type"]), json.dumps(get_config(key)))
