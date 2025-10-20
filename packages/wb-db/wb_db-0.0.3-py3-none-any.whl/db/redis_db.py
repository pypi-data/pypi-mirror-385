from __future__ import annotations

from furl import furl
from redis import Redis

from db.db import DB


class RedisDB(DB):
    """
    import db


    redis_db = db.RedisDB.from_uri("redis://:@localhost:6379/0?encoding=utf-8&decode_responses=True")

    redis_db = db.RedisDB(
        host="localhost",
        port=6379,
        password=None,
        dbname=0
    )
    """

    def __init__(
            self,
            host: str = "localhost",
            port: int = 6379,
            password: str | None = None,
            dbname: int = 0,
            encoding: str = "utf-8",
            decode_responses: bool = True
    ) -> None:
        self._host = host
        self._port = port
        self._password = password
        self._dbname = dbname
        self._encoding = encoding
        self._decode_responses = decode_responses

        self._redis: Redis | None = None

    def _open(self) -> None:
        self._redis = self.open_connect()

    def _close(self) -> None:
        self.close_connect(self._redis)

    def open_connect(self) -> Redis:
        return Redis(
            host=self._host,
            port=self._port,
            db=self._dbname,
            password=self._password,
            encoding=self._encoding,
            decode_responses=self._decode_responses
        )

    @staticmethod
    def close_connect(redis: Redis | None = None) -> None:
        if redis is not None:
            redis.close()

    @classmethod
    def from_uri(cls, uri: str) -> RedisDB:
        f = furl(uri)
        return cls(
            host=f.host,
            port=int(f.port),
            password=f.password,
            dbname=int(f.path.segments[0]),
            encoding=f.query.params.get("encoding", "utf-8"),
            decode_responses=eval(f.query.params.get("decode_responses", True))
        )

    @property
    def redis(self) -> Redis:
        return self._redis
