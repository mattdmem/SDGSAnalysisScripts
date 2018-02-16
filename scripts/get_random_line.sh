#!/bin/sh
set -- junk $(awk -v SEED=$$ 'BEGIN { srand(SEED) } { print rand(),$0 }' | sort -n | head -12000)
shift 2
echo "$@" | sed 's/file /\n/g' | cut -f1 -d" "
