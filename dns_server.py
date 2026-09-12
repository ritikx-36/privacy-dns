import socket
from concurrent.futures import ThreadPoolExecutor

import dns.message
import dns.rcode
import dns.rdatatype

from config import (
    SERVER_HOST,
    SERVER_PORT,
    UPSTREAM_DNS,
    BUFFER_SIZE,
    UPSTREAM_TIMEOUT,
    MAX_WORKERS
)

from filter import (
    load_domains,
    load_filter_directory,
    check_domain
)

from cache import (
    set_cache,
    get_cache,
    cleanup_cache
)

from stats import (
    increment,
    get_stats
)


server = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

server.bind(
    (SERVER_HOST, SERVER_PORT)
)

print(
    f"DNS server running on {SERVER_HOST}:{SERVER_PORT}"
)


# Load allowlist
allowed_domains = load_domains(
    "allowlist.txt"
)


# Load blocklist
blocked_domains = load_domains(
    "blocklist.txt"
)


# Load all filter files
filter_domains = load_filter_directory(
    "filters"
)


# Combine all blocked domains
blocked_domains.update(
    filter_domains
)


def handle_request(data, address):

    print(
        "Received DNS request from:",
        address
    )

    # Count every DNS request
    increment("total_queries")


    # Clean expired cache entries
    cleanup_cache()


    # Parse DNS query
    try:

        query = dns.message.from_wire(
            data
        )

    except Exception:

        print(
            "Invalid DNS request"
        )

        return


    # Extract domain
    try:

        domain = query.question[0].name.to_text()

        domain = domain.rstrip(".").lower()

    except Exception:

        print(
            "Could not extract domain"
        )

        return


    print(
        "Domain:",
        domain
    )


    # Extract query type
    try:

        query_type = dns.rdatatype.to_text(
            query.question[0].rdtype
        )

    except Exception:

        print(
            "Could not determine query type"
        )

        return


    print(
        "Query type:",
        query_type
    )


    # Check filtering rules
    result = check_domain(
        domain,
        allowed_domains,
        blocked_domains
    )


    # Block domain
    if result == "BLOCK":

        print(
            "BLOCKED:",
            domain
        )

        increment(
            "blocked_queries"
        )

        response = dns.message.make_response(
            query
        )

        response.set_rcode(
            dns.rcode.NXDOMAIN
        )

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

        print(
            "CACHE HIT:",
            domain,
            query_type
        )

        increment(
            "cache_hits"
        )

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
    print(
        "CACHE MISS:",
        domain,
        query_type
    )

    increment(
        "cache_misses"
    )


    # Create upstream socket
    upstream = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    upstream.settimeout(
        UPSTREAM_TIMEOUT
    )


    try:

        upstream.sendto(
            data,
            UPSTREAM_DNS
        )

        response, _ = upstream.recvfrom(
            BUFFER_SIZE
        )


    except socket.timeout:

        print(
            "UPSTREAM DNS TIMEOUT:",
            domain
        )

        increment(
            "upstream_failures"
        )

        # Return SERVFAIL
        response = dns.message.make_response(
            query
        )

        response.set_rcode(
            dns.rcode.SERVFAIL
        )

        server.sendto(
            response.to_wire(),
            address
        )

        upstream.close()

        return


    except OSError as error:

        print(
            "UPSTREAM DNS ERROR:",
            error
        )

        increment(
            "upstream_failures"
        )

        # Return SERVFAIL
        response = dns.message.make_response(
            query
        )

        response.set_rcode(
            dns.rcode.SERVFAIL
        )

        server.sendto(
            response.to_wire(),
            address
        )

        upstream.close()

        return


    upstream.close()


    # Read actual TTL from DNS response
    try:

        dns_response = dns.message.from_wire(
            response
        )

        ttl = 60

        if dns_response.answer:

            ttl = dns_response.answer[0].ttl

        print(
            "TTL:",
            ttl
        )


        # Store response in cache
        set_cache(
            domain,
            query_type,
            response,
            ttl
        )


    except Exception:

        print(
            "Invalid response from upstream"
        )


    # Send response to client
    server.sendto(
        response,
        address
    )


def print_statistics():

    current_stats = get_stats()

    print()
    print("DNS Statistics")
    print("--------------------")
    print(
        "Total queries:",
        current_stats["total_queries"]
    )
    print(
        "Blocked queries:",
        current_stats["blocked_queries"]
    )
    print(
        "Cache hits:",
        current_stats["cache_hits"]
    )
    print(
        "Cache misses:",
        current_stats["cache_misses"]
    )
    print(
        "Upstream failures:",
        current_stats["upstream_failures"]
    )
    print()


# Create worker pool
executor = ThreadPoolExecutor(
    max_workers=MAX_WORKERS
)


while True:

    data, address = server.recvfrom(
        BUFFER_SIZE
    )

    executor.submit(
        handle_request,
        data,
        address
    )