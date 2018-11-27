from twitter import UserClient

keys = [
    ["m7iea1YPA1Rb82kkTkUDDGX5h", "raptWufk8kNxQtunHsJsJAuduG6cRWfFpFaik6aHwC91yIntjm", "804426829041762304-qHw59MmMK8KsedUaDc3ochNYOzGwVEi", "OSiNGoic7dQdB1uFOhZFsIq7j5cEkmewjR5Ob8JmoagLf"]
]


class TwitterCredentials(object):
    def __init__(self, i=0):
        self._key = keys[i]
        self.CONSUMER_KEY = self._key[0]
        self.CONSUMER_SECRET = self._key[1]
        self.ACCESS_TOKEN = self._key[2]
        self.ACCESS_TOKEN_SECRET = self._key[3]


class TwitterClient(object):
    def __init__(self):
        self._twitter_credentials = None
        self._client = None
        self._i = 0

    def get_user_client(self):
        self._twitter_credentials = TwitterCredentials(self._i % 1)
        self._client = UserClient(self._twitter_credentials.CONSUMER_KEY, self._twitter_credentials.CONSUMER_SECRET,
                                  self._twitter_credentials.ACCESS_TOKEN, self._twitter_credentials.ACCESS_TOKEN_SECRET)
        self._i += 1
        return self._client