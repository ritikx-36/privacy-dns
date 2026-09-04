import time


cache = {}


def set_cache(domain, query_type, response, ttl):

    key = (domain, query_type)

    expires_at = time.time() + ttl

    cache[key] = {
        "response": response,
        "expires_at": expires_at
    }


def get_cache(domain, query_type):

    key = (domain, query_type)

    if key not in cache:
        return None

    entry = cache[key]

    if time.time() >= entry["expires_at"]:

        del cache[key]

        return None

    return entry["response"]