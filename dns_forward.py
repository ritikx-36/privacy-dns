import socket

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.settimeout(3)

data = b""

server.sendto(data, ("1.1.1.1", 53))
