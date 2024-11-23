cc=$1
predelay=$2
postdelay=$3
linkspeed=$4
buffsize=$5
file=$6

./clean.sh

./simnet.sh $cc $predelay $postdelay $linkspeed $buffsize $file

#rm -f index*
