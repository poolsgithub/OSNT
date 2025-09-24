#!/bin/bash

# Exit on any error
set -e

sudo su

# Namespace names

# Create namespaces
ip netns add NS1
ip netns add NS2
ip netns add NS3

echo "created namespaces"

# Create veth pairs
ip link add veth1 type veth peer name veth2
ip link add veth3 type veth peer name veth4

# Assign veth ends to namespaces
ip link set veth1 netns NS1
ip link set veth2 netns NS2
ip link set veth3 netns NS2
ip link set veth4 netns NS3

# Assign IP addresses
ip netns exec NS1 ip addr add 10.0.1.1/24 dev veth1
ip netns exec NS2 ip addr add 10.0.1.2/24 dev veth2
ip netns exec NS2 ip addr add 10.0.2.1/24 dev veth3
ip netns exec NS3 ip addr add 10.0.2.2/24 dev veth4

echo "assigned ip"

# Bring up interfaces and loopback

ip netns exec NS1 ip link set lo up
ip netns exec NS2 ip link set lo up
ip netns exec NS3 ip link set lo up


ip netns exec NS1 ip link set veth1 up
ip netns exec NS2 ip link set veth2 up
ip netns exec NS2 ip link set veth3 up
ip netns exec NS3 ip link set veth4 up

# Set up routing
ip netns exec NS1 ip route add default via 10.0.1.2
ip netns exec NS3 ip route add default via 10.0.2.1

echo "Network namespaces and veth links are set up"

#enable forwarding
ip netns exec NS2 sysctl -w net.ipv4.ip_forward=1

#generate the certificates using openssl 
openssl req -x509 -newkey rsa:2048 -keyout server.key -out server.crt -days 365 -nodes

#on NS1 can be NS3 also
ip netns exec NS1 openssl s_client -dtls -connect 10.0.2.2:4444

#on NS3 can be NS1 also
ip netns exec NS3 openssl s_server -dtls -accept 4444 -cert server.crt -key server.key

#on NS2 to view packets 
ip netns exec NS2 tcpdump -i any -n udp



