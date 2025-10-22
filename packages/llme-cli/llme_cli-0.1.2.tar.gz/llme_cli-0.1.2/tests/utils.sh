#!/bin/bash

# Common setup and useful functions for test scripts

export SUITE=$(basename "$0" .sh)
export TESTDIR=$(dirname "$0")
export ORIGDIR=`pwd`

# The llme tool to check
LLME="llme"
if ! command -v "$LLME"; then
	echo "llme not found: $LLME" >&2
fi

# run before each test. override if needed
setup() {
	true
}

# run after each test. override if needed
teardown() {
	true
}

# copy files from data to the workdir
copy() {
	for f in "$@"; do
		cp -r "$TESTDIR/data/$f" "$WORKDIR/"
	done
}


# Register a test result
result() {
	config="$ORIGDIR/$LOGDIR/config.json"
	url=`jq -r .base_url "$config"`
	model=`jq -r .model "$config"`
	chat="$ORIGDIR/$LOGDIR/chat.json"
	msgs=`jq '.|length' "$chat"`
	words=`wc -w < "$chat"`

	echo "$SUITE,$task,$url,$model,$1,$2,$msgs,$words" >> "$ORIGDIR/$LOGDIR/result.csv"
	case $1 in
		ERROR*|FAIL*|TIMEOUT*)
			color=91;;
		PASS*)
			color=92;;
		*)
			color=93;;
	esac
	echo -e "\e[${color}m$1\e[0m $2 $LOGDIR/ model=$model msgs=$msgs words=$words"
}

# Check that the llm result matches the pattern $1 on the last line.
answer() {
	if tail -n1 "$LOGDIR/log.txt" | grep -x "$1"; then
		result "PASS"
	elif grep -i "$1" "$LOGDIR/log.txt"; then
		result "ALMOST"
	else
		result "FAIL"
	fi
}

# Check that the llm result talk about a pattern
smoke() {
	if grep -i "$1" "$LOGDIR/log.txt"; then
		result "PASS"
	else
		result "FAIL"
	fi
}

# Run llme in its workdir with a fresh python environment
runllme() {
	(
	set -e
	cd "$WORKDIR"
	python -m venv venv
	. venv/bin/activate
	timeout -v -f -sINT 60 "$LLME" "$@"
)
}

# Run a test with the llme tool
# Usage: tllme taskname [llme args...] (use "$@" for args)
#
# define '$V' for verbose
# define '$F' to filter tests
# define '$KEEPWORKDIR' to reuse the workdir in subsequent tests
tllme() {
	task=$1
	shift

	if [ -n "$F" ] && ! echo "$task" | grep "$F"; then
		return 1
	fi

	cd "$ORIGDIR"

	# Tests results are stored in logs/$id/ where id is a unique identifier
	id=$SUITE-$task-$(date +%s)
	echo "$id" >&2
	export LOGDIR="logs/$id"
	mkdir -p "$LOGDIR"
	env | grep "^LLME_" > "$LOGDIR/env.txt"

	export LLME_CHAT_OUTPUT=$ORIGDIR/$LOGDIR/chat.json
	export LLME_BATCH=true
	export LLME_YOLO=true

	# create a tmp workdir
	if [ -z "$WORKDIR" ] || [ -z "$KEEPWORKDIR" ]; then
		WORKDIR=`mktemp --tmpdir -d llme-XXXXX`
	fi
	ln -s "$WORKDIR" "$LOGDIR/workdir"

	setup

	if [ -z "$V" ]; then
		out=/dev/null
	else
		out=/dev/stdout
	fi

	"$LLME" "$@" --dump-config > "$LOGDIR/config.json"
	runllme "$@" > >(tee "$LOGDIR/log.txt" > "$out") 2>&1
	err=$?

	teardown

	if [ "$err" -eq 124 ]; then
		result "TIMEOUT"
		return 124
	elif [ "$err" -ne 0 ]; then
		grep --color -i error "$LOGDIR/log.txt"
		result "ERROR"
		return $err
	fi

	return 0
}
