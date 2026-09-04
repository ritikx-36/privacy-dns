import socket
from concurrent.futures import ThreadPoolExecutor

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


def handle_request(data, address):

    print("Received DNS request from:", address)


    # Clean expired cache entries
    cleanup_cache()


    # Parse DNS query
    try:

        query = dns.message.from_wire(data)

    except Exception:

        print("Invalid DNS request")

        return


    # Extract domain
    try:

        domain = query.question[0].name.to_text()

        domain = domain.rstrip(".").lower()

    except Exception:

        print("Could not extract domain")

        return


    print("Domain:", domain)


    # Extract query type
    try:

        query_type = dns.rdatatype.to_text(
            query.question[0].rdtype
        )

    except Exception:

        print("Could not determine query type")

        return


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

        return


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

        return


    # Cache miss
    print("CACHE MISS:", domain, query_type)


    # Forward request to upstream DNS
    upstream = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    upstream.settimeout(3)


    try:

        upstream.sendto(
            data,
            ("1.1.1.1", 53)
        )

        response, _ = upstream.recvfrom(4096)

    except socket.timeout:

        print("UPSTREAM DNS TIMEOUT:", domain)

        response = dns.message.make_response(query)

        response.set_rcode(dns.rcode.SERVFAIL)

        server.sendto(
            response.to_wire(),
            address
        )

        upstream.close()

        return

    except OSError as error:

        print("UPSTREAM DNS ERROR:", error)

        response = dns.message.make_response(query)

        response.set_rcode(dns.rcode.SERVFAIL)

        server.sendto(
            response.to_wire(),
            address
        )

        upstream.close()

        return


    upstream.close()


    # Read actual TTL from DNS response
    try:

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

    except Exception:

        print("Invalid response from upstream")


    # Send response to client
    server.sendto(
        response,
        address
    )


# Create a pool of worker threads
executor = ThreadPoolExecutor(max_workers=10)


while True:

    data, address = server.recvfrom(4096)

    executor.submit(
        handle_request,
        data,
        address
    )