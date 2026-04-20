from pubtor.utils.connectdb import ConnectDB

class Pubtor():
    
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

    

