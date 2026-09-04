import time


cache = {}


def set_cache(domain, response, ttl):

    expires_at = time.time() + ttl

    cache[domain] = {
        "response": response,
        "expires_at": expires_at
    }


def get_cache(domain):

    if domain not in cache:
        return None

    entry = cache[domain]

    if time.time() >= entry["expires_at"]:

        del cache[domain]

        return None

    return entry["response"]

