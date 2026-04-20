import psycopg2

from pathlib import Path

from pubtor.db.mrconso import MRCONSO


class ConnectDB:
    
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

    # Context manager support
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
