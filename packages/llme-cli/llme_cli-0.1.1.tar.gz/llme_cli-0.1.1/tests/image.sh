#!/bin/bash

. "$(dirname "$0")/utils.sh"

tllme "20" "What is in this image?" "$@" < image.png
tllme "21" image.png "What is in this image?" "$@"
tllme "22" "What is in this image?" image.png "$@"
tllme "23" "What is in this image? image.png" "$@"

tllme "31" bonjour "exécute la commande uptime" "calcule la factorielle de 10" "résume en 10 (dix) mots le fichier" README.md "décrit en 10 (dix) mot l'image" image.png "hello" "$@"
