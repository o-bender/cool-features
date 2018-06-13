#!/usr/bin/env python3

import socket
import struct
import configparser
import re


def wake_on_lan(ipaddress, macaddress):
    # Check macaddress format and try to compensate.
    macaddress = ''.join(re.findall('[0-9a-fA-F]+', macaddress))
    if len(macaddress) != 12:
        raise ValueError('Incorrect MAC address format')

    # Pad the synchronization stream.
    data = ''.join(['FFFFFFFFFFFF', macaddress * 16])
    send_data = b''

    # Split up the hex values and pack.
    for i in range(0, len(data), 2):
        send_data = b''.join(
            [send_data, struct.pack('B', int(data[i: i + 2], 16))])

    # Broadcast it to the LAN.
    print(send_data)
    return
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(send_data, (ipaddress, 7))


def loadConfig():
	""" Read in the Configuration file to get CDN specific settings	"""
	config = configparser.ConfigParser()
	config.read('wol_config.ini')
	return config


if __name__ == '__main__':
    config = loadConfig()
    broadcast = config['General']['broadcast']
    for section in config:
        print('Wol was send to', section)
        mac = config[section].get('mac')
        if mac:
            ipaddress = config[section].get('ipaddress', broadcast)
            wake_on_lan(ipaddress, mac)
