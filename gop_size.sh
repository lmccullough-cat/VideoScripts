#!/bin/sh

ffprobe -show_frames "$1" > output.txt 

GOP=0;

while read p; do
  if [ "$p" = "key_frame=0" ]
  then
    GOP=$((GOP+1))
  fi

if [ "$p" = "key_frame=1" ]
then
  GOP=$((GOP+1))
  echo $GOP
  GOP=0;
fi

done < output.txt

