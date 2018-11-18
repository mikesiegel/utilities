#!/usr/bin/python
import socket
import fcntl
import struct
import sys
import os

"""
  Ping sweeps an IP range given an interface name.
  Uses no external modules so it's nice and portable ;)

  Usage: python scan.py eth0
  
  by @ml_siegel
"""

def ip_to_hex(ip_address):
  """
    Converts string IP to hex

    args:
      ip_address (str): IP address in dotted quad

    returns:
      string: string representation of hex
  """
  hex_ip = [hex(int(x)) for x in ip_address.split('.')]
  hex_ip = [str(x)[2:].zfill(2) for x in hex_ip]
  return int("0x{}".format(str.join('',hex_ip)), 16)

def mask_to_hostcount(netmask):
  """
    Converts string netmask to host count

    args:
      netmask (str): netmask in dotted quad

    returns:
      int: number of hosts in subnet
  """
  cidr = sum([bin(int(x)).count('1') for x in netmask.split('.')])
  return (2**(32 - cidr)) - 2

def scan_subnet(hex_subnet, host_number):
  """
     Ping sweeps a subnet. Takes advantage of ping accepting hex.

     args:
       hex_subnet(str): String represenmtation of hex network host_number
       host_number(int): Integer of number of hosts in network

  """

  count = 0
  first_host = int(hex(hex_subnet + 1),16)
  last_host = int(hex(hex_subnet + host_number),16)
  print("Ping sweeping {} to {}".format(hex(first_host), hex(last_host)))
  count = first_host
  while count < last_host:
      os.system('ping -c 1 {}'.format(hex(count)))
      count = count + 1

def get_ip_address(ifname):
    """
      Gets an IP address from interface name. Modified stackoverflow solution
      to work with 3.x

      args:
        ifname (str): The name of an interface i.e. eth0

        returns:
          if_address (string): Interface IP in dotted quad
          if_netmask (string): Interface netmask in dotted quad
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # from sockios.h
    SIOCGIFADDR = 0x8915
    SIOCGIFNETMASK = 0x891b
    print("ver {}".format(sys.version_info[1]))
    if sys.version_info[0] == 3:
        if_address = socket.inet_ntoa(fcntl.ioctl(
          s.fileno(),
          SIOCGIFADDR,
          struct.pack('256s', bytes(ifname[:15], 'utf-8'))
          )[20:24])
        if_netmask = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            SIOCGIFNETMASK,
            struct.pack('256s', bytes(ifname[:15], 'utf-8'))
            )[20:24])
    elif sys.version_info[0] == 2:
       if_address = socket.inet_ntoa(fcntl.ioctl(
           s.fileno(),
           SIOCGIFADDR,
           struct.pack('256s', ifname[:15])
            )[20:24])
            if_netmask = socket.inet_ntoa(fcntl.ioctl(
                    s.fileno(),
                    SIOCGIFNETMASK,
                    struct.pack('256s', ifname[:15])
                    )[20:24])

    return if_address, if_netmask

def main():
  if_address, if_netmask = get_ip_address(sys.argv[1])
  host_number = mask_to_hostcount(if_netmask)
  hex_ip = ip_to_hex(if_address)
  hex_netmask = ip_to_hex(if_netmask)
  print("Scanning inteface {} with IP {} and mask {}".format(sys.argv[1], if_address, if_netmask))
  scan_subnet((int(hex(hex_ip),16) & int(hex(hex_netmask),16)), host_number)

if __name__ == "__main__":
    main()
