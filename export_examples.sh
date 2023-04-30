#!/bin/bash
FILES="examples/*_RAW.sub"
for f in $FILES
do
  fo=${f%_RAW.*}
  fo_ct="$fo""_ct.csv"
  fo_ct_cs="$fo""_ct_cs.csv"
  fo_decode="$fo""_decoded.txt"

  python3 subdecode.py $f -ct -o $fo_ct
  python3 subdecode.py $f -ct -cs -o $fo_ct_cs
  python3 subdecode.py $f -o $fo_decode
done