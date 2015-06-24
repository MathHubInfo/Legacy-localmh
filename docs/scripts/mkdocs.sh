#!/usr/bin/env bash

python generate_config_doc.py
cd .. && echo $(pwd) && mkdocs "$@"
