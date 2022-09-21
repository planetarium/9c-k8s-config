#!/usr/bin/env bash
set -ex

pushd 9c-main
    ./deploy-main.sh
popd

pushd 9c-onboarding
    ./deploy-headless.sh
popd
