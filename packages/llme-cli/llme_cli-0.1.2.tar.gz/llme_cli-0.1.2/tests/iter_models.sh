#!/bin/bash

. "$(dirname "$0")/utils.sh"
url=`$LLME --dump-config | jq -r '.base_url'`

models=`curl -s "$url/models" | jq '.. | .id? | select(. != null)' -r`
models=`echo $models`

echo "models: $models"
for LLME_MODEL in $models; do
    echo >&1 "$LLME_MODEL"
    export LLME_MODEL
    "$@"
done 
