#!/usr/bin/env bash

set -e
set -x

mypy toolbelt
black toolbelt tests --check
isort toolbelt tests --check-only
