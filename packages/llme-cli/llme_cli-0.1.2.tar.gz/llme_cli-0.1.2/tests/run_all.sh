#!/bin/sh

# you are in for a threat!
d="$(dirname "$0")"

$d/smoketest.sh "$@"
$d/smokeimages.sh "$@"
$d/basic_answers.sh "$@"
$d/patch_file.sh "$@"
$d/hello.sh "$@"
