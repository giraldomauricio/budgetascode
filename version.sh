#!/bin/bash

# The only argument is empty or "mayor".
arg=$1
# Split
hash=$(git rev-parse --short HEAD)
IFS='.'
version_str=`cat VERSION.TXT`
read -a strarr <<< "$version_str"
mayor_version=${strarr[0]}
minor_version=${strarr[1]}
if [ "$arg" == "mayor" ]; then
  mayor_version="$((mayor_version + 1))"
  minor_version=0
else
  minor_version="$((minor_version + 1))"
fi
echo "$mayor_version.$minor_version.$hash" > VERSION.TXT