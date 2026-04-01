import psycopg2

class connectdb():
    
    def __init__(self, conn=None):
        self.conn = conn
        self.cur = conn.cursor()
    
    @classmethod
    def connect(cls, 
                dbname="umls_db", 
                user="user",
                password="pass",
                host="localhost",
                port=5432
                ):
        
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,  # or "umls_postgres" if using docker network
            port=port
        )
        
        return cls(conn)
    
    def execute(self, query, params=None):
        self.cur.execute(query, params)
        self.conn.commit()
        
    def fetchall(self):
        return self.cur.fetchall()
    
    def close(self):
        self.cur.close()
        self.conn.close()

    # Context manager support
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

class run():
    
    # Using try/finally
    db = connectdb.connect()
    try:
        db.execute("CREATE TABLE IF NOT EXISTS umls_concepts (cui VARCHAR(10) PRIMARY KEY, name TEXT, definition TEXT)")
    finally:
        db.close()


    # Using with statement (recommended)
    with connectdb.connect() as db:
        db.execute("INSERT INTO umls_concepts (cui, name, definition) VALUES (%s, %s, %s)",
                ("C0000005", "Aspirin", "A common painkiller"))
        db.execute("SELECT * FROM umls_concepts")
        rows = db.fetchall()
        print(rows)
    # Automatically closes connection and cursor