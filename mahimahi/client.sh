#!/bin/bash
sudo ifconfig ingress mtu 100
sudo sysctl net.ipv4.tcp_sack=0
echo "Launching client..."
cc=$1
link=$2


#sudo echo "0" > /proc/sys/net/ipv4/tcp_sack
# sudo tcpdump -i ingress -w aft-btl-test.pcap &
# iperf3 -c [IP_SERVER} -p 2500 -C $cc -t 60 -R --connect-timeout 2000 -M 100
#sudo sysctl net.ipv4.tcp_congestion_control=$1
#iperf -c [IP_SERVER] -p 5000 -t 30 -Z $1
#wget -U Mozilla https://www.youtube.com/ -O index
#wget -U Mozilla https://open.spotify.com/user/deutschegrammophon/playlist/2B11k6zJ2vIJTjOiqz3Y35 -O index
wget -U Mozilla $link -O index --timeout 75
#wget -U Mozilla https://www.instagram.com/static/bundles/es6/FeedPageContainer.js/434e5de15e7c.js -O index
# wget -U Mozilla https://www.reddit.com/r/AskReddit/comments/brlti4/reddit_what_are_some_underrated_apps/ -O index


echo cc: $cc
echo link: $link 

sleep 1
echo "DONE!"

sudo killall tcpdump
sudo killall mm-link mm-delay
