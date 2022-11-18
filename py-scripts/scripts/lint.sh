#!/usr/bin/env bash

set -e
set -x

mypy toolbelt
black toolbelt tests --check  --line-length=89
isort toolbelt tests --check-only
