from twitter import UserClient
from time import sleep

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


class EmptyApiResponse:
    def __init__(self):
        self.data = {}


class TwitterClient(object):
    def __init__(self):
        self._twitter_credentials = None
        self._i = 0
        self._try_count = 1
        self._client = self._get_new_user_client()
        self.sleep_time = 10

    def _get_new_user_client(self):
        self._twitter_credentials = TwitterCredentials(self._i % 1)
        self._client = UserClient(self._twitter_credentials.CONSUMER_KEY, self._twitter_credentials.CONSUMER_SECRET,
                                  self._twitter_credentials.ACCESS_TOKEN, self._twitter_credentials.ACCESS_TOKEN_SECRET)
        self._i += 1
        return self._client

    def lists_memberships_get(self, screen_name, count, cursor):
        for i in range(self._try_count):
            try:
                response = self._client.api.lists.memberships.get(screen_name=screen_name, count=count, cursor=cursor)
                if response is None:
                    return EmptyApiResponse()
                return response
            except Exception as err:
                print(err)
                sleep(self.sleep_time)
                self._get_new_user_client()

        print("Error {} times, moving to the next user.".format(self._try_count))
        return EmptyApiResponse()

    def lists_members_get(self, list_id, count, cursor):
        for i in range(self._try_count):
            try:
                response = self._client.api.lists.members.get(list_id=list_id, count=count, cursor=cursor)
                if response is None:
                    return EmptyApiResponse()
                return response
            except Exception as err:
                print(err)
                sleep(self.sleep_time)
                self._get_new_user_client()

        print("Error {} times, moving to the next user.".format(self._try_count))
        return EmptyApiResponse()

    def statuses_user_timeline_get(self, screen_name, count):
        for i in range(self._try_count):
            try:
                response = self._client.api.statuses.user_timeline.get(screen_name=screen_name, count=count, tweet_mode='extended')
                if response is None:
                    return EmptyApiResponse()
                return response
            except Exception as err:
                print(err)
                sleep(self.sleep_time)
                self._get_new_user_client()

        print("Error {} times, moving to the next user.".format(self._try_count))
        return EmptyApiResponse()

