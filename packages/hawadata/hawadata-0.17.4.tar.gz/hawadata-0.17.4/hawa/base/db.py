from contextlib import contextmanager

import MySQLdb
import sqlalchemy
from redis.client import StrictRedis

from hawa.base.decos import singleton
from hawa.config import project

metadata = sqlalchemy.MetaData()


@singleton
class DbUtil:
    _conn = None
    _cursor_conn = None
    _engine_conn = None

    @property
    def db_engine(self):
        database_url = (
            f"{project.DB_MODE}://{project.DB_USER}:{project.DB_PSWD}@{project.DB_HOST}/"
            f"{project.DB_NAME}?charset=utf8"
        )
        engine = sqlalchemy.create_engine(database_url, pool_pre_ping=True)
        return engine

    @contextmanager
    def engine_conn(self):
        self._engine_conn = self.db_engine.connect()
        yield self._engine_conn
        self._engine_conn.close()

    @staticmethod
    def connect():
        return MySQLdb.connect(
            host=project.DB_HOST,
            port=project.DB_PORT,
            user=project.DB_USER,
            passwd=project.DB_PSWD,
            db=project.DB_NAME,
        )

    @property
    def cursor(self):
        """only for test"""
        return self.cursor_conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    @property
    def cursor_conn(self):
        if not self._cursor_conn:
            self._cursor_conn = self.connect()
        if not self._cursor_conn.open:
            self._cursor_conn = self.connect()
        # is self._cursor_conn alive?
        try:
            self._cursor_conn.ping()
        except Exception as e:
            self._cursor_conn = self.connect()
        return self._cursor_conn

    def query_by_sql(self, sql: str, mode: str = "all"):
        """
        :param sql:
        :param mode: all or one
        :return: list or dict by mode
        """
        with self.cursor_conn.cursor(cursorclass=MySQLdb.cursors.DictCursor) as cursor:
            cursor.execute(sql)
            match mode:
                case "all":
                    return cursor.fetchall()
                case "one":
                    return cursor.fetchone()


@singleton
class RedisUtil:
    @property
    def conn(self):
        return StrictRedis(
            host=project.REDIS_HOST,
            db=project.REDIS_DB,
            decode_responses=True,
        )
