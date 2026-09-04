import socket
import dns.message
import dns.rcode
import dns.rdatatype

from filter import load_domains, load_filter_directory, check_domain
from cache import set_cache, get_cache, cleanup_cache


server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind(("127.0.0.1", 8053))

print("DNS server running on 127.0.0.1:8053")


# Load allowlist
allowed_domains = load_domains("allowlist.txt")


# Load blocklist
blocked_domains = load_domains("blocklist.txt")

# Load all filter files
filter_domains = load_filter_directory("filters")

# Combine all blocked domains
blocked_domains.update(filter_domains)


while True:

    data, address = server.recvfrom(512)

    print("Received DNS request from:", address)


    # Clean expired cache entries
    cleanup_cache()


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


    # Parse DNS query
    query = dns.message.from_wire(data)

    query_type = dns.rdatatype.to_text(
        query.question[0].rdtype
    )

    print("Query type:", query_type)


    # Check filtering rules
    result = check_domain(
        domain,
        allowed_domains,
        blocked_domains
    )


    # Block domain
    if result == "BLOCK":

        print("BLOCKED:", domain)

        response = dns.message.make_response(query)

        response.set_rcode(dns.rcode.NXDOMAIN)

        server.sendto(
            response.to_wire(),
            address
        )

        continue


    # Check cache
    cached_response = get_cache(
        domain,
        query_type
    )


    if cached_response is not None:

        print("CACHE HIT:", domain, query_type)

        # Replace cached transaction ID
        # with current request ID
        cached_response = (
            data[:2] +
            cached_response[2:]
        )

        server.sendto(
            cached_response,
            address
        )

        continue


    # Cache miss
    print("CACHE MISS:", domain, query_type)


    # Forward request to upstream DNS
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

    upstream.close()


    # Read actual TTL from DNS response
    dns_response = dns.message.from_wire(response)

    ttl = 60

    if dns_response.answer:

        ttl = dns_response.answer[0].ttl

    print("TTL:", ttl)


    # Store response in cache
    set_cache(
        domain,
        query_type,
        response,
        ttl
    )


    # Send response to client
    server.sendto(
        response,
        address
    )