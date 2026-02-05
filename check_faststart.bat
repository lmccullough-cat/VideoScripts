for i in *.mp4
do
  echo $i
  head -c 4096 "$i" >TEMP.mp4
  ffmpeg -v trace -i TEMP.mp4 NUL 2>"$i.txt"
  grep -L -m 1 -e "type:'moov'" "$i.txt" >>OUTPUT.txt
  rm "$i.txt"
  rm TEMP.mp4
done

