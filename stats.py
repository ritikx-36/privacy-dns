import json
import threading


stats = {
    "total_queries": 0,
    "blocked_queries": 0,
    "cache_hits": 0,
    "cache_misses": 0,
    "upstream_failures": 0
}


stats_lock = threading.Lock()


def increment(name):

    with stats_lock:

        stats[name] += 1


def get_stats():

    with stats_lock:

        return stats.copy()


def get_stats_json():

    with stats_lock:

        return json.dumps(
            stats,
            indent=4
        )