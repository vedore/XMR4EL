from pathlib import Path
from pubtor.db.mrconso import MRCONSO
from pubtor.utils.connectdb import ConnectDB

class Pubtor:
    BASE_DIR = Path(__file__).resolve().parent.parent
    QUERIES_DIR = BASE_DIR / "queries"

    params = {
        "dbname": "umls_db",
        "user": "user",
        "password": "pass",
        "host": "localhost",
        "port": 5432
        }

    def __init__(self,
                 params=params):
        
        self.params = params
        self.conn = ConnectDB.connect()

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
    

