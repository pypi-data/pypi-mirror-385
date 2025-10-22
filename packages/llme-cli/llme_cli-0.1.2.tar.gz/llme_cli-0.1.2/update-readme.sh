#!/bin/bash

set -e
{
sed -n '1,/^<!--help-->$/p' README.md
echo '```console'
echo '$ llme --help'
llme --help
echo '```'
sed -n '/^<!--\/help-->$/,$p' README.md
} > README.new.md
mv README.new.md README.md
