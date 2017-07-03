#! /usr/bin/env python3

import socket

target_host = "192.168.1.151"
target_port = 9999

# creat a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to server
client.connect((target_host, target_port))

# send data
client.send("hello".encode('utf-8'))

# receive data
response = client.recv(4096)

print(response.decode('utf-8'))

client.close()
