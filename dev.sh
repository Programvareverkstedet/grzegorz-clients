#!/bin/bash
if ! which entr > /dev/null; then
    echo "entr is not installed, aborting..."
    exit 1
fi

find . -name "*.py" | entr -r ./main.py
