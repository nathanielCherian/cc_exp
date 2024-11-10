echo available congestion control: $(sysctl net.ipv4.tcp_available_congestion_control)
#ccs=(reno cubic bbr htcp bic scalable illinois westwood vegas yeah veno)
ccs=(reno cubic bbr)
for cc in "${ccs[@]}"; do
	echo "Working on $cc"
	sudo sysctl -w net.ipv4.tcp_congestion_control=$cc
	python3 cc_exp.py $1 $cc
done
