from pubtor.models.concept import Concept


class UMLSKnowledgeBase:
    def __init__(self, repo):
        self.repo = repo

    def get_concept(self, cui):
        names = self.repo.get_names_by_cui(cui)
        defs = self.repo.get_definitions_by_cui(cui)
        stys = self.repo.get_semantic_types_by_cui(cui)
        rels = self.repo.get_relations_by_cui(cui)

        return Concept(
            cui=cui,
            names=[x.string for x in names],
            definitions=[x.definition for x in defs],
            semantic_types=[x.sty for x in stys],
            relations=[
                {
                    "rel": r.rel,
                    "rela": r.rela,
                    "target_cui": r.cui2 if r.cui1 == cui else r.cui1
                }
                for r in rels
            ]
        )