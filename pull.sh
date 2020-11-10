#!/bin/bash

echo "Pull brick or lab ${1} ..."
what=${1}
if ["$wahrt" == "core"]; then
    python3 ./src/gpm.py --pull-gws ${1}
else
    python3 ./src/gpm.py --pull ${1}
fi

