#!/bin/bash

# $1 is output path of notify wait

# This is to compensate for inotify recursive option
# not seeming to work.
find .  -not -type d > ./files_to_watch_list.txt

inotifywait -e open -m --fromfile=./files_to_watch_list.txt -o $1 &

shift

# Creating this directory as a hack in the script rather than modifying the
# output option of the compilation line.
mkdir -p bazel-out/k8-fastbuild/bin/src/_objs/a/
$@
