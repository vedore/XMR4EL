import psycopg2

from pathlib import Path

from pubtor.db.mrconso import MRCONSO


class ConnectDB:
    BASE_DIR = Path(__file__).resolve().parent.parent
    QUERIES_DIR = BASE_DIR / "queries"
    
    def __init__(self, conn=None):
        self.conn = conn
        self.cur = conn.cursor()
    
    @classmethod
    def connect(
        cls, 
        dbname="umls_db", 
        user="user",
        password="pass",
        host="umls_postgres",
        port=5432
        ):
        
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        
        return cls(conn)
    
    def search_one(self, query_file, params):
        query = self.load_sql(query_file)
        self.cur.execute(query, params)
        return self.cur.fetchone()

    def find_mrconso_by_cui(self, cui):
        row = self.search_one("find_mrconso_by_cui.sql", (cui, ))
        return MRCONSO(*row) if row else None
    
    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    @classmethod
    def load_sql(cls, filename: str) -> str:
        return (cls.QUERIES_DIR / filename).read_text(encoding="utf-8")

    # Context manager support
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
