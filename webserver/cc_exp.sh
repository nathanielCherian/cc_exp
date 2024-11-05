echo available congestion control: $(sysctl net.ipv4.tcp_available_congestion_control)
ccs=(reno cubic bbr htcp bic scalable illinois westwood vegas yeah veno)
for cc in "${ccs[@]}"; do
	echo "Working on $cc"
	sudo sysctl -w net.ipv4.tcp_congestion_control=$cc
	python3 cc_exp.py "/users/cheriann/cc_exp/webserver/ccexp_pcaps" $cc
done
