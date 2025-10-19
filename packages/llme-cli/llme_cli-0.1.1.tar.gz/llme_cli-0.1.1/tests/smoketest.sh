#!/bin/bash

. "$(dirname "$0")/utils.sh"

tllme "01" "What is the capital of France?" "$@"
tllme "02" "What is the capital of France?" "What about Canada?" "And Vatican?" "And Mordor?" "And my axe?" "$@"
tllme "03" "What the content on the current directory?" "$@"
tllme "04" "What is the current operating system?" "$@"
tllme "05" "What is the factorial of 153?" "$@"
tllme "06" "Summarize the README.md file in one sentence" "$@"

tllme "10" "Summarize the file README.md in one sentence" "$@"
tllme "11" "Summarize the file in one sentence" "$@" < README.md
tllme "12" README.md "Summarize the file in one sentence" "$@"
tllme "13" "Summarize the file in one sentence" "$@" README.mg

tllme "31" bonjour "exécute la commande uptime" "calcule la factorielle de 10" "résume en 10 (dix) mots le fichier" README.md "$@"

tllme "32" -o tmp.json "Tell me a joke about LLMs" "$@"
tllme "33" -i tmp.json "What is the joke about?" "$@"
