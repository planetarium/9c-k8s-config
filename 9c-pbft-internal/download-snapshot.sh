#!/usr/bin/env bash

base_url=${1:-https://9c-snapshot-dev.s3.us-east-2.amazonaws.com/9c-pbft-internal}
save_dir=${2:-"9c-main-snapshot_$(date +%Y%m%d_%H)"}

echo "Start download snapshot"
# strip tailing slash
base_url=${base_url%/}

function get_snapshot_value() {
    snapshot_json_url="$1"
    snapshot_param="$2"

    snapshot_param_return_value=$(curl --silent "$snapshot_json_url" | jq ".$snapshot_param")
    echo "$snapshot_param_return_value"
}

function download_unzip_full_snapshot() {
    snapshot_json_filename="latest.json"
    snapshot_zip_filename="state_latest.zip"
    snapshot_zip_filename_array=("$snapshot_zip_filename")

    while :
    do
        snapshot_json_url="$base_url/$snapshot_json_filename"
        echo "$snapshot_json_url"

        BlockEpoch=$(get_snapshot_value "$snapshot_json_url" "BlockEpoch")
        TxEpoch=$(get_snapshot_value "$snapshot_json_url" "TxEpoch")
        PreviousBlockEpoch=$(get_snapshot_value "$snapshot_json_url" "PreviousBlockEpoch")
        PreviousTxEpoch=$(get_snapshot_value "$snapshot_json_url" "PreviousTxEpoch")

        snapshot_zip_filename="snapshot-$BlockEpoch-$TxEpoch.zip"
        snapshot_zip_filename_array+=("$snapshot_zip_filename")

        if [ "$PreviousBlockEpoch" -eq 0 ]
        then
            break
        fi

        snapshot_json_filename="snapshot-$PreviousBlockEpoch-$PreviousTxEpoch.json"
    done

    if [[ ! -d "$save_dir" ]]
    then
        echo "[Info] The directory $save_dir does not exist and is created."
        mkdir -p "$save_dir"
    fi

    for ((i=${#snapshot_zip_filename_array[@]}-1; i>=0; i--))
    do
        snapshot_zip_filename="${snapshot_zip_filename_array[$i]}"
        rm "$snapshot_zip_filename" 2>/dev/null

        snapshot_zip_url="$base_url/$snapshot_zip_filename"
        echo "$snapshot_zip_url"

        wget -q "$snapshot_zip_url"
        echo "Unzipping $snapshot_zip_filename"
        unzip -o "$snapshot_zip_filename" -d "$save_dir"
        rm "$snapshot_zip_filename"
    done
}

download_unzip_full_snapshot

# The return value for the program that calls this script
echo "$save_dir"
