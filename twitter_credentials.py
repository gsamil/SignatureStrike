
keys = [
    ["WXtT7Lq4MHHvmK8XPNn9QiY1Y", "bOWycGRKctXM9Ruu8PW9d5RPcoML9oHf7ejaDTitC2xKP0BcdD", "1682690833-dPp9i07U7KF6vIXsBQGRcRQdgMrnmsYmJow8dGI", "rUnNF8jpPVPafCwk95ePGEv2vIDq5cegdEu2FBaI8QUgq"],
    ["qlc8OG6rjrQjE9ma67NBoa499", "rty8ljZoGw3RczIzuVaMk1YRyUehyVWL0OXuJMoCf9daElidXg", "312689218-daicXyON4HgquS5MxnWlNDnSSinsHee0SNRADY8B", "OWaXOFBHTYNeVowLDYrdmc1ocGTE9ysrGzoMlNxOuu2yO"],
    ["Xn6kq5wHjt8JExlvqHDlWyFsf", "4nuYyqgtR0CjqIzigsuTplU9BudJFdBNI87OJRYzpAPHbk7lu4", "802615980-C5NL3A9zKCYS25Q9V4L7ksGkU424NAI6nnLf8Nzb", "Be18CvylrX9xBR1VK6vIZ3jnBNw4bm5JkoWyBobRwoCyb"],
    ["qEgHKHnL55g7k4U9xihiCzdVj", "QcUDHJS04wK5hrmlxV5C4gweiRPDca9JQoc4gp7ftHOTgZAdbf", "863573499436122112-LA60oJLBzwVnhZjGOUPzRsJcU1wYzs9", "8CKFpp6qyxkAk1KfjW7kMRqJPoHKloppPrvd7Tjiwllyk"],
    ["m7iea1YPA1Rb82kkTkUDDGX5h", "raptWufk8kNxQtunHsJsJAuduG6cRWfFpFaik6aHwC91yIntjm", ]
]


class TwitterCredentials(object):
    def __init__(self, i):
        self._key = keys[i]
        self.CONSUMER_KEY = self._key[0]
        self.CONSUMER_SECRET = self._key[1]
        self.ACCESS_TOKEN = self._key[2]
        self.ACCESS_TOKEN_SECRET = self._key[3]
