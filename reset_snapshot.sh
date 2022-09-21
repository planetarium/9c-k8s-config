#!/usr/bin/env bash
set -ex

apt -y update
apt -y install curl
apt -y install zip

HOME="/app"
DATA_PATH="/data"
STORE_PATH="/data/$1"
BACKUP_PATH="/data/backup"
STS_NAME=$2
CHAIN_SUFFIX="$(date -d "+9 hour" -u +"%Y%m%d%H%M")"
mkdir -p "$BACKUP_PATH"

function copy_store() {
  if [ -d "$STORE_PATH" ]; then
    echo "$STORE_PATH exists."
    chmod 777 -R "$STORE_PATH"
    cd "$STORE_PATH"
    zip -r "$BACKUP_PATH/$STS_NAME-$CHAIN_SUFFIX".zip . -i .
  else 
    echo "$STORE_PATH does not exist. Creating $STORE_PATH."
    mkdir "$STORE_PATH"
  fi
}

function clean_backup() {
  ls -1tr $BACKUP_PATH/* | head -n -3 | xargs -d '\n' rm -f --
}

function clear_store() {
  if [ -d "$STORE_PATH" ]; then
    echo "$STORE_PATH exists."
    rm -r "$STORE_PATH/"
    mkdir "$STORE_PATH"
  else 
    echo "$STORE_PATH does not exist. Creating $STORE_PATH."
    mkdir "$STORE_PATH"
  fi
}

function download_and_setup_snapshot() {
  curl "https://download.nine-chronicles.com/v100027/9c-main-snapshot.zip" -o "$DATA_PATH/snapshot.zip"
  unzip "$DATA_PATH/snapshot.zip" -d "$STORE_PATH"
  chmod 777 -R "$STORE_PATH"
  rm "$DATA_PATH/snapshot.zip"
}

trap '' HUP

copy_store
clean_backup
clear_store
download_and_setup_snapshot
