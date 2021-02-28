#!/bin/bash

echo "Push brick or lab ${1} (with tag name ${2})..."
python3 ./src/gpm.py --push ${1} ${2}
