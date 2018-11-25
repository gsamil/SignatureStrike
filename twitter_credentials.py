
keys = [
    ["m7iea1YPA1Rb82kkTkUDDGX5h", "raptWufk8kNxQtunHsJsJAuduG6cRWfFpFaik6aHwC91yIntjm", "804426829041762304-qHw59MmMK8KsedUaDc3ochNYOzGwVEi", "OSiNGoic7dQdB1uFOhZFsIq7j5cEkmewjR5Ob8JmoagLf"]
]


class TwitterCredentials(object):
    def __init__(self, i):
        self._key = keys[i]
        self.CONSUMER_KEY = self._key[0]
        self.CONSUMER_SECRET = self._key[1]
        self.ACCESS_TOKEN = self._key[2]
        self.ACCESS_TOKEN_SECRET = self._key[3]
