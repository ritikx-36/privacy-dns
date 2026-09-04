import socket

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind(("127.0.0.1", 8053))

print("DNS server running on 127.0.0.1:8053")

while True:
    data, address = server.recvfrom(512)

    print("Received DNS request from:", address)

    upstream = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    upstream.settimeout(3)

    upstream.sendto(data, ("1.1.1.1", 53))

    response, _ = upstream.recvfrom(512)

    server.sendto(response, address)

    upstream.close()