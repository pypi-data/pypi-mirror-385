from __future__ import annotations

from urllib.parse import quote_plus

from furl import furl
from pymongo import MongoClient
from pymongo.database import Database

from db.db import DB


class MongoDB(DB):
    """
    import db


    mongo_db = db.MongoDB.from_uri("mongodb://localhost:27017/db")

    mongo_db = db.MongoDB(
        host="localhost",
        port=27017,
        username=None,
        password=None,
        dbname="db"
    )
    """

    def __init__(
            self,
            host: str = "localhost",
            port: int = 27017,
            username: str | None = None,
            password: str | None = None,
            dbname: str | None = None
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._dbname = dbname

        self._client: MongoClient | None = None
        self._db: Database | None = None

    def _open(self) -> None:
        self._client, self._db = self.open_connect()

    def _close(self) -> None:
        self.close_connect(self._client)

    def open_connect(self) -> tuple[MongoClient, Database]:
        if self._username is not None and self._password is not None:
            uri = "mongodb://%s:%s@%s:%s/" % (
                quote_plus(self._username),
                quote_plus(self._password),
                self._host,
                self._port
            )
        else:
            uri = "mongodb://%s:%s/" % (self._host, self._port)

        client = MongoClient(uri)
        db = client[self._dbname]
        return client, db

    @staticmethod
    def close_connect(client: MongoClient | None = None) -> None:
        if client is not None:
            client.close()

    @classmethod
    def from_uri(cls, uri: str) -> MongoDB:
        f = furl(uri)
        return cls(
            host=f.host,
            port=int(f.port),
            username=f.username,
            password=f.password,
            dbname=f.path.segments[0]
        )

    @property
    def client(self) -> MongoClient:
        return self._client

    @property
    def db(self) -> Database:
        return self._db
