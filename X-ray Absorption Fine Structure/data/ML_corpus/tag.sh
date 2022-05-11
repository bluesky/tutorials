#!/usr/bin/env bash

allcsv=`ls *.csv`
echo "file,tag" > tags.txt
for f in $allcsv; do
    gnuplot -e "pl \"<sed 's/,/ /g' $f | sed -e '/time/ s/^#*/#/'\" u 2:3; pause 1" &
    echo -n "Score? (0=bad, 1=good) "
    read SCORE
    echo $f, $SCORE >> tags.txt
done

##pl "<sed 's/,/ /g' d5fc5c13.csv | sed -e '/time/ s/^#*/#/'" u 2:3
