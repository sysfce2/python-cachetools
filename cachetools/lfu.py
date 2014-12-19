from .cache import Cache
from .decorators import cachedfunc
from .lock import RLock

import collections
import operator


class LFUCache(Cache):
    """Least Frequently Used (LFU) cache implementation.

    This class counts how often an item is retrieved, and discards the
    items used least often to make space when necessary.

    """

    def __init__(self, maxsize, missing=None, getsizeof=None):
        Cache.__init__(self, maxsize, missing, getsizeof)
        self.__counter = collections.Counter()

    def __getitem__(self, key, cache_getitem=Cache.__getitem__):
        value = cache_getitem(self, key)
        self.__counter[key] += 1
        return value

    def __setitem__(self, key, value, cache_setitem=Cache.__setitem__):
        cache_setitem(self, key, value)
        self.__counter[key] += 1

    def __delitem__(self, key, cache_delitem=Cache.__delitem__):
        cache_delitem(self, key)
        del self.__counter[key]

    def popitem(self):
        """Remove and return the `(key, value)` pair least frequently used."""
        try:
            key = min(self.__counter.items(), key=operator.itemgetter(1))[0]
        except ValueError:
            raise KeyError('cache is empty')
        return key, self.pop(key)


def lfu_cache(maxsize=128, typed=False, getsizeof=None, lock=RLock):
    """Decorator to wrap a function with a memoizing callable that saves
    up to `maxsize` results based on a Least Frequently Used (LFU)
    algorithm.

    """
    return cachedfunc(LFUCache(maxsize, getsizeof), typed, lock)