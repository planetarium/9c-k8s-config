#!/bin/sh -e
set -x

black toolbelt tests
isort toolbelt tests
