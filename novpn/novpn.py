import sys
import socket 

"""
Sends command to the vpn proccess to run cmd
in split tunnel.
"""
client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
client.connect("\0vpn")
client.send(f'split {"".join(sys.argv[1:])}'.encode())
client.close()
