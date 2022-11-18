#!/bin/sh -e
set -x

isort toolbelt tests
black toolbelt tests  --line-length=89
