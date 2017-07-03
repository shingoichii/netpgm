#! /usr/bin/env python3

import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(5)

print("[*] listening on {}:{}".format(bind_ip, bind_port))

def handle_client(client_socket):
    request = client_socket.recv(1024)
    print("[*] received: {}".format(request.decode('utf-8')))
    client_socket.send("ACK".encode('utf-8'))
    client_socket.close()

while True:
    (client, addr) = server.accept()
    print("[*] accepted connection from {}:{}".format(addr[0], addr[1]))
    client_hander = threading.Thread(target=handle_client, args=(client,))
    client_hander.start()
