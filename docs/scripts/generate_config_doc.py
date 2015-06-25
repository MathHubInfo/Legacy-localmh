#!/usr/bin/env python

import json

decoder = json.JSONDecoder()

with open("../../lmh/data/config.json") as f:
    data = decoder.decode(f.read())

out = """#List of configuration Settings

This is a list of all configuration settings to be used with [lmh config](../commands/config). 


| Name |  | Type | Default |
| ------------ | ------------- | ------------ | ------------ |
"""

for key in sorted(data.keys()):
    value = data[key]
    try:
        if value["hidden"]:
            continue
    except:
        pass
    out += "| "+key + " | " + value["help"].strip() + " | " + value["type"] + " | " + str(value["default"])+" |\n"

f = open("../docs/generated/config.md", "w+")
f.write(out)
f.close()
