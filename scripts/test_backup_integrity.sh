#!/bin/sh
list1=/tmp/list1
list2=/tmp/list2
shuflist=/tmp/shuflist
n=100000 # How many files to compare.
if test ! -d "$1" -o ! -d "$2"; then
    echo "Usage: $0 path1 path2"
    exit 1
fi
exitcode=0
(cd "$1" && find . -type f >"$list1") || exit 1
(cd "$2" && find . -type f >"$list2") || exit 1
if cmp -s "$list1" "$list2"; then
    shuf -n "$n" "$list1" > "$shuflist"
    while IFS= read -r filename; do
        if ! cmp -s "$1/$filename" "$2/$filename"; then
            echo "Files '$1/$filename' and '$2/$filename' differ."
            exitcode=1
            break
        fi
    done < "$shuflist"
else
    echo File lists differ.
    exitcode=1
fi
rm "$list1" "$list2" "$shuflist"
exit $exitcode