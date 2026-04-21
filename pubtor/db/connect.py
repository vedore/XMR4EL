import psycopg2

from pathlib import Path


class Database:
    BASE_DIR = Path(__file__).resolve().parent.parent
    QUERIES_DIR = BASE_DIR / "queries"

    def __init__(self, params):
        if params is None:
            raise ValueError("params cannot be None")

        self.params = params
        self.conn = psycopg2.connect(
            dbname=params["dbname"],
            user=params["user"],
            password=params["password"],
            host=params["host"],
            port=params["port"]
        )
        self.cur = self.conn.cursor()

    @classmethod
    def load_sql(cls, filename: str) -> str:
        return (cls.QUERIES_DIR / filename).read_text(encoding="utf-8")

    def fetch_one(self, query_file, params=None):
        query = self.load_sql(query_file)
        self.cur.execute(query, params or ())
        return self.cur.fetchone()

    def fetch_all(self, query_file, params=None):
        query = self.load_sql(query_file)
        self.cur.execute(query, params or ())
        return self.cur.fetchall()

    def execute(self, query_file, params=None):
        query = self.load_sql(query_file)
        self.cur.execute(query, params or ())
        self.conn.commit()

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.close()
