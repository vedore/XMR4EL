from pathlib import Path

from pubtor.models.mrconso import MRCONSO
from pubtor.models.mrdef import MRDEF
from pubtor.models.mrrel import MRREL
from pubtor.models.mrsty import MRSTY


class UMLSRepository:
    BASE_DIR = Path(__file__).resolve().parent.parent
    QUERIES_DIR = BASE_DIR / "queries"

    def __init__(self, db):
        self.db = db

    def get_names_by_cui(self, cui):
        rows = self.db.fetch_all("mrconso/find_by_cui.sql", (cui,))
        return [MRCONSO.from_row(row) for row in rows]

    def get_definitions_by_cui(self, cui):
        rows = self.db.fetch_all("mrdef/find_by_cui.sql", (cui,))
        return [MRDEF.from_row(row) for row in rows]

    def get_semantic_types_by_cui(self, cui):
        rows = self.db.fetch_all("mrsty/find_by_cui.sql", (cui,))
        return [MRSTY.from_row(row) for row in rows]

    def get_relations_by_cui(self, cui):
        rows = self.db.fetch_all("mrrel/find_by_cui1_or_cui2.sql", (cui, cui))
        return [MRREL.from_row(row) for row in rows]