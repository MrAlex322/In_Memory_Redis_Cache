import json
import atexit
import os

CACHE_FILE_PATH = "cache.json"


def save_cache_to_disk(cache):
    cache_data = {}
    for key, value in cache.items():
        cache_data[key] = value
    with open("cache.json", "w") as f:
        json.dump(cache_data, f)


def load_cache_from_disk(cache):
    if os.path.exists("cache.json") and os.path.getsize("cache.json") > 0:
        with open("cache.json", "r") as f:
            cache_data = json.load(f)
            for key, value in cache_data.items():
                cache[key] = value


def register_cache_atexit(cache):
    atexit.register(save_cache_to_disk, cache)
    load_cache_from_disk(cache)
