#!/bin/bash
# @ml_siegel
# usage: ./scan.sh eth0
# NOTE: /bin/sh interpreter WILL NOT work, requires bash.

ip_to_hex()
{
# convert IP array to hex
IP=($@)
hex_ip="0x"
for count in `seq 0 3`;
do
  hex_octet=`echo "obase=16; ${IP[$count]}" | bc`
  # zero padding
  if [ ${#hex_octet} == 1 ];
      then
  hex_octet="0$hex_octet"
  fi
  hex_ip="$hex_ip$hex_octet"
done
echo $hex_ip
}

create_mask()
{
  # convert CIDR notation to a mask. ie 24 -> 255.255.255.0
  declare CIDR=$1
  bin_mask=""
  for count in `seq 1 $CIDR`;
  do
    bin_mask="$bin_mask""1"
  done
  for count in `seq 1 $(expr 32 - $CIDR)`;
  do
    bin_mask="$bin_mask""0"
  done
  echo $bin_mask
}

bin_to_hex()
{
  # convert a binary mask to hex
  declare BIN=$1
  hex_ip=`echo "ibase=2;obase=10000; $BIN" | bc`
  echo $hex_ip
}

scan_subnet()
{
  # scan our subnet. We can take advantage of the fact ping accepts hex!
  declare SUBNET=$1
  declare HOSTS=$2
  first_host=`echo "ibase=16;obase=10; $SUBNET + 1" | bc`
  last_host=`echo "ibase=16;obase=10; $SUBNET + $HOSTS" | bc`
  echo "Ping sweeping $first_host to $last_host"
  declare count=$first_host
  while [[ "0x$count" -lt "0x$last_host" ]];
  do
    ping -c 1 0x$count
    count=`echo "ibase=16;obase=10; $count + 1" | bc`
  done
}

cidr=$(ip -o -f inet addr show $1 | awk '/scope global/ {print $4}')
# Read the cidr notation into an array consisting of IP and mask
IFS='/' read -ra ADDR <<< "$cidr"
# calculater the number of possible hosts in the subnet
exponent=`expr 32 - ${ADDR[1]}`
hosts=`(expr $((2**$exponent)) - 2)`
# split our IP into an array based on octets
IFS="." read -ra IP <<< "${ADDR[0]}"
hex_ip=$(ip_to_hex "${IP[@]}")
bin_mask=$(create_mask ${ADDR[1]})
hex_mask=$(bin_to_hex $bin_mask)
hex_mask="0x$hex_mask"
# calculate the network address of our current subnet
network=`echo "obase=16; $((hex_ip & hex_mask))" | bc`
echo "Scanning network $cidr on interface $1"
scan_subnet $network $hosts
