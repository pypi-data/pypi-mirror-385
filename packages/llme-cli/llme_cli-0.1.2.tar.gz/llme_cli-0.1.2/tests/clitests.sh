#!/bin/bash

set -xe
for config in *.toml; do
	"$config" = "pyproject.toml" && continue

	llme 'hello' 'world' -c "$config" -b >/dev/null
	llme <<<'hello' 'world' -c "$config" -b >/dev/null
	llme <<<'hello' -c "$config" -b >/dev/null
	llme -v -v --config "$config" --dump-config > dumpconfig.txt
	! llme -m bad hello
	! llme -u bad hello
	! llme --bad hello
	! llme -c bad hello
done
