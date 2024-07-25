from collections import OrderedDict

cache = OrderedDict()
cache_max_size = 500


def get_from_cache(key):
    if key in cache:
        value = cache.pop(key)
        cache[key] = value
        return value
    return None


def put_in_cache(key, value):
    if len(cache) >= cache_max_size:
        cache.popitem(last=False)
    cache[key] = value