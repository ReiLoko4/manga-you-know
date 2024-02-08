from functools import lru_cache, wraps

from cachetools import cached


def conditional_cache_ttl(*cache_args, **cache_kwargs):
    def decorator(func):
        func = cached(*cache_args, **cache_kwargs)(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, bool):
                cache = cache_args[0]
                key = cache_kwargs['key'](args, kwargs) if 'key' in cache_kwargs else args
                cache.pop(key, None)
            return result

        return wrapper

    return decorator

def conditional_cache_lru(maxsize=128):
    def decorator(func):
        cached_func = lru_cache(maxsize=maxsize)(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = cached_func(*args, **kwargs)
            if isinstance(result, bool):
                return func(*args, **kwargs)
            return result

        return wrapper

    return decorator

# ChatGPT gave it for me :( 
# I'm not that smart
