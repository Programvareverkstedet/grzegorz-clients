#!/usr/bin/env bash
if ! command -v entr > /dev/null; then
    echo "entr is not installed, aborting..."
    exit 1
fi

git ls-files | poetry run entr -r grzegorz-webui "$@"
