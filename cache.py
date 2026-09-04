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


def cleanup_cache():

    current_time = time.time()

    expired_keys = []

    for key, entry in cache.items():

        if current_time >= entry["expires_at"]:
            expired_keys.append(key)

    for key in expired_keys:

        del cache[key]