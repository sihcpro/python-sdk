import os
import threading

import pymongo


class BaseClient:
    connection_template = "mongodb+srv://{}:{}@{}/{}?retryWrites=true&w=majority"
    aws_connection_template = "mongodb+srv://{}/test?authSource=$external&authMechanism=MONGODB-AWS&retryWrites=true&w=majority"
    __cache_client = {}
    __cache_lock = threading.Lock()

    def __init__(self, username, password, host, use_cache=True, aws=False):
        self._aws = aws
        self._use_cache = use_cache
        if aws:
            self.config = {
                "username": None,
                "password": None,
                "host": host,
                "use_cache": use_cache,
                "aws": aws,
            }
            self.connection_str = self.aws_connection_template.format(host)
        else:
            self.config = {
                "username": username,
                "password": password,
                "host": host,
                "use_cache": use_cache,
            }
            self.connection_str = self.connection_template.format(
                username, password, host
            )

    @classmethod
    def load_from_env(cls, use_cache=True):
        """
        This load the credential from the following 3 env variables
        MONGO_USERNAME
        MONGO_PASSWORD
        MONGO_HOST
        """
        host = os.getenv("MONGO_HOST")
        aws = os.getenv("AWS")
        if aws:
            if host is None:
                raise Exception("Require Env Variable Host is None. %s")
            return cls(None, None, host, use_cache, aws=True)
        else:
            username = os.getenv("MONGO_USERNAME")
            password = os.getenv("MONGO_PASSWORD")
            if username is None or password is None or host is None:
                raise Exception(
                    "Require Env Variable is None. %s %s" % (username, host)
                )
            return cls(username, password, host, use_cache)

    def get_client(self):
        if self._use_cache:
            if self.connection_str not in self.__cache_client:
                with self.__cache_lock:
                    if self.connection_str not in self.__cache_client:
                        self.__cache_client[self.connection_str] = pymongo.MongoClient(
                            self.connection_str, connect=False
                        )
            return self.__cache_client[self.connection_str]
        else:
            return pymongo.MongoClient(self.connection_str)
