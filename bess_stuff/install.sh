# Use cloudlab node with ubuntu 18.04 (default python 2.7)
sudo apt-get update
sudo apt install make apt-transport-https ca-certificates g++ make pkg-config libunwind8-dev liblzma-dev zlib1g-dev libpcap-dev libssl-dev libnuma-dev git python python-pip python-scapy libgflags-dev libgoogle-glog-dev libgraph-easy-perl libgtest-dev libgrpc++-dev libprotobuf-dev libc-ares-dev libbenchmark-dev libgtest-dev protobuf-compiler-grpc

pip install --user "protobuf<=3.17.3" grpcio scapy

sudo sysctl vm.nr_hugepages=1024

# clone and build BESS
# Don't forget to start daemon!
