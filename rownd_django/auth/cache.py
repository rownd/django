import asyncio
from django.core.cache import cache
import time

class RowndCache:
    def fetch(self, cache_key: str, return_val_fn: any, ttl: int):
        cache_val = cache.get(cache_key)
        if cache_val is None:
            return_val = return_val_fn()
            cache.set(cache_key, [return_val, time.time()])
            return return_val
        else:
            return_val = cache_val[0]
            last_fetch_time = cache_val[1]

            # Start a new thread to update the cached value if the TTL is exceeded
            if time.time() - last_fetch_time > ttl:
              new_val = return_val_fn()
              if new_val:
                asyncio.run(self.cache_set_coroutine(cache_key, [new_val, time.time()]))
            
            return return_val

    @asyncio.coroutine
    def cache_set_coroutine(self, cache_key: str, cache_val: any):
        cache.set(cache_key, cache_val)
