ffmpeg -v trace -i $1 2>&1 | grep -e type:\'mdat\' -e type:\'moov\'
