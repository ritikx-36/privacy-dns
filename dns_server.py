import socket
import dns.message
import dns.rcode

from filter import load_domains, check_domain


server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind(("127.0.0.1", 8053))

print("DNS server running on 127.0.0.1:8053")


# Load allowlist
allowed_domains = load_domains("allowlist.txt")


# Load blocklists
blocked_domains = load_domains("blocklist.txt")

ads = load_domains("filters/ads.txt")
trackers = load_domains("filters/trackers.txt")


# Combine all blocked domains
blocked_domains = blocked_domains | ads | trackers


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


    # Ask the rule engine
    result = check_domain(
        domain,
        allowed_domains,
        blocked_domains
    )


    # Block domain
    if result == "BLOCK":

        print("BLOCKED:", domain)

        query = dns.message.from_wire(data)

        response = dns.message.make_response(query)

        response.set_rcode(dns.rcode.NXDOMAIN)

        server.sendto(response.to_wire(), address)

        continue


    # Allow domain
    print("ALLOWED:", domain)


    # Forward allowed request
    upstream = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    upstream.settimeout(3)

    upstream.sendto(
        data,
        ("1.1.1.1", 53)
    )

    response, _ = upstream.recvfrom(512)

    server.sendto(response, address)

    upstream.close()