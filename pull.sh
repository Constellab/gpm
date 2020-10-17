#!/bin/bash

echo "Pull brick or lab ${1} ..."
python3 ./src/gpm.py --pull ${1}
