from pubtor.models.mrconso import MRCONSO
from pubtor.models.mrdef import MRDEF
from pubtor.models.mrrel import MRREL
from pubtor.models.mrsty import MRSTY


class UMLSRepository:
    def __init__(self, db):
        self.db = db

    def get_names_by_cui(self, cui):
        rows = self.db.search_all("mrconso/find_by_cui.sql", (cui,))
        return [MRCONSO(*row) for row in rows]

    def get_definitions_by_cui(self, cui):
        rows = self.db.search_all("mrdef/find_by_cui.sql", (cui,))
        return [MRDEF(*row) for row in rows]

    def get_semantic_types_by_cui(self, cui):
        rows = self.db.search_all("mrsty/find_by_cui.sql", (cui,))
        return [MRSTY(*row) for row in rows]

    def get_relations_by_cui(self, cui):
        rows = self.db.search_all("mrrel/find_by_cui1_or_cui2.sql", (cui, cui))
        return [MRREL(*row) for row in rows]