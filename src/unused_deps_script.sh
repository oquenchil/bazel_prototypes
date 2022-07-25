#!/bin/bash

# Cleans up inotifywait output to just the file path
cat $4 | sed 's|./\(.*\) OPEN.*|\1|g' > used_files_patterns.txt

# $3 contains a list of pairs with target,path_to_file_from_target
# We get the list of targets actually used.
grep -f used_files_patterns.txt $3 | cut -d, -f1 | sort -u > used_targets.txt

cut -d, -f1 $3 > all_targets.txt

# Lines unique only to all_targets.txt (i.e. unused targets)
comm -23  all_targets.txt used_targets.txt > unused_targets.txt

touch $2

# Could be just one buildozer command.
while read p; do
  echo "buildozer 'remove deps $p' $1" >> $2
done <unused_targets.txt
