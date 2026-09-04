import socket
import dns.message
import dns.rcode

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind(("127.0.0.1", 8053))

print("DNS server running on 127.0.0.1:8053")


# Load blocklist
blocked_domains = set()

with open("blocklist.txt", "r") as file:
    for line in file:
        domain = line.strip().lower()

        if domain:
            blocked_domains.add(domain)


# Load allowlist
allowed_domains = set()

with open("allowlist.txt", "r") as file:
    for line in file:
        domain = line.strip().lower()

        if domain:
            allowed_domains.add(domain)


while True:

    data, address = server.recvfrom(512)

    print("Received DNS request from:", address)

    # DNS header = 12 bytes
    i = 12
    domain = ""

    while data[i] != 0:
        length = data[i]

        i += 1

        domain += data[i:i + length].decode()

        i += length

        domain += "."

    domain = domain.rstrip(".").lower()

    print("Domain:", domain)


    # Check allowlist first
    allowed = False

    for allowed_domain in allowed_domains:

        if domain == allowed_domain:
            allowed = True
            break

        if domain.endswith("." + allowed_domain):
            allowed = True
            break


    if allowed:

        print("ALLOWLISTED:", domain)

    else:

        # Check blocklist
        blocked = False

        for blocked_domain in blocked_domains:

            if domain == blocked_domain:
                blocked = True
                break

            if domain.endswith("." + blocked_domain):
                blocked = True
                break


        # Block domain
        if blocked:

            print("BLOCKED:", domain)

            query = dns.message.from_wire(data)

            response = dns.message.make_response(query)

            response.set_rcode(dns.rcode.NXDOMAIN)

            server.sendto(response.to_wire(), address)

            continue


        print("ALLOWED:", domain)


    # Forward allowed request
    upstream = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    upstream.settimeout(3)

    upstream.sendto(data, ("1.1.1.1", 53))

    response, _ = upstream.recvfrom(512)

    server.sendto(response, address)

    upstream.close()