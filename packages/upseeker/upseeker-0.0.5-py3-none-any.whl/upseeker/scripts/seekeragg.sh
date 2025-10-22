#!/usr/bin/bash

#echo "SEEKERAGG CALLED WITH ARGUMENTS $1 $2 $3 $4"

for (( c=0; c< $4 ; c++ )) do
  sleep 2
  outFiles=$(find $1 -name out\*.file -printf '%P,')
  ${SeekerPath}/bin/coll-linux $1 $2 $3 ${outFiles}
done


