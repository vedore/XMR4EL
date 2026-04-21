

# main.py

"""
Pseudo-code structure for an end-to-end UMLS Entity Linking pipeline.

Goal:
1. Receive a text mention
2. Normalize it
3. Search candidates in MRCONSO
4. Enrich each candidate with MRDEF, MRSTY, MRREL
5. Build features
6. Rank candidates
7. Return the best concept
"""

import json

from pubtor.db.connect import Database
from pubtor.repository.repo import UMLSRepository
from pubtor.kb.kb import UMLSKnowledgeBase


def normalize_mention(text: str) -> str:
    """
    Pseudo-code:
    - lowercase
    - strip whitespace
    - optionally remove punctuation
    - optionally normalize accents
    """
    normalized = text.strip().lower()
    return normalized


def retrieve_candidates(kb: UMLSKnowledgeBase, mention: str, limit: int = 20):
    """
    Pseudo-code:
    - search MRCONSO.STR
    - use exact match / trigram / full-text search
    - return candidate concepts or candidate CUIs
    """
    candidates = kb.search_candidates(mention, limit=limit)
    return candidates


def enrich_candidate(kb: UMLSKnowledgeBase, cui: str):
    """
    Pseudo-code:
    - fetch all important KB information for one concept
    - names
    - definitions
    - semantic types
    - relations / graph neighbors
    """
    concept = kb.get_concept(cui)
    return concept


def build_features(mention: str, concept):
    """
    Pseudo-code:
    Create ranking features for one candidate.

    Possible features:
    - exact string match
    - normalized string similarity
    - preferred name match
    - overlap between mention and aliases
    - semantic type compatibility
    - definition similarity
    - graph/context features
    """

    features = {
        "cui": concept.cui,
        "exact_match": False,
        "preferred_name_match": False,
        "alias_overlap_score": 0.0,
        "definition_score": 0.0,
        "semantic_type_score": 0.0,
        "graph_score": 0.0,
        "final_score": 0.0,
    }

    # Example pseudo-logic
    if concept.names:
        if mention in [name.lower() for name in concept.names]:
            features["exact_match"] = True

    # Placeholder scoring logic
    if features["exact_match"]:
        features["final_score"] += 1.0

    return features


def rank_candidates(feature_rows: list[dict]) -> list[dict]:
    """
    Pseudo-code:
    - sort candidates by final_score descending
    - later this could be replaced by an ML/XMR ranking model
    """
    ranked = sorted(feature_rows, key=lambda x: x["final_score"], reverse=True)
    return ranked


def link_mention(kb: UMLSKnowledgeBase, mention: str):
    """
    Full entity linking flow for one mention.
    """

    print(f"\nInput mention: {mention}")

    # 1. Normalize input
    normalized_mention = normalize_mention(mention)
    print(f"Normalized mention: {normalized_mention}")

    # 2. Retrieve candidate CUIs / concepts
    candidates = retrieve_candidates(kb, normalized_mention, limit=10)

    if not candidates:
        print("No candidates found.")
        return None

    print(f"Candidates retrieved: {len(candidates)}")

    # 3. Enrich each candidate
    enriched_candidates = []
    for candidate in candidates:
        # candidate could already be a concept or just contain a CUI
        cui = candidate.cui if hasattr(candidate, "cui") else candidate["cui"]

        concept = enrich_candidate(kb, cui)
        if concept is not None:
            enriched_candidates.append(concept)

    if not enriched_candidates:
        print("No enriched candidates available.")
        return None

    # 4. Build ranking features
    feature_rows = []
    for concept in enriched_candidates:
        features = build_features(normalized_mention, concept)
        feature_rows.append(features)

    # 5. Rank
    ranked = rank_candidates(feature_rows)

    if not ranked:
        print("Ranking produced no result.")
        return None

    best = ranked[0]
    best_cui = best["cui"]

    # 6. Recover the best concept object
    best_concept = kb.get_concept(best_cui)

    # 7. Return final prediction
    result = {
        "mention": mention,
        "normalized_mention": normalized_mention,
        "best_cui": best_cui,
        "best_score": best["final_score"],
        "concept": best_concept,
        "ranking": ranked,
    }

    return result


def pretty_print_result(result):
    """
    Pseudo-code for output formatting.
    """
    if result is None:
        print("\nNo entity linked.")
        return

    concept = result["concept"]

    print("\n=== ENTITY LINKING RESULT ===")
    print(f"Mention: {result['mention']}")
    print(f"Normalized: {result['normalized_mention']}")
    print(f"Best CUI: {result['best_cui']}")
    print(f"Score: {result['best_score']}")

    if concept:
        print("\n--- Concept information ---")
        print(f"CUI: {concept.cui}")

        if getattr(concept, "names", None):
            print(f"Names: {concept.names[:5]}")

        if getattr(concept, "definitions", None):
            print(f"Definitions: {concept.definitions[:3]}")

        if getattr(concept, "semantic_types", None):
            print(f"Semantic types: {concept.semantic_types[:5]}")

        if getattr(concept, "relations", None):
            print(f"Relations: {concept.relations[:5]}")

def get_db_params():
    db_file = "./db_params.json"
    with open(db_file, "r") as fin:
        db_params = json.load(fin)
    return db_params

def main():
    """
    Main application flow.
    """

    # Example input mention
    mention = "aspirin"

    db_params = get_db_params()

    # Open DB connection
    with Database(db_params) as db:

        print(db)

        # Create repository
        repo = UMLSRepository(db)

        # Create KB service
        kb = UMLSKnowledgeBase(repo)

        ct = kb.get_concept("C0000005")

        print(ct)

        # Run entity linking

        # Show output


if __name__ == "__main__":
    main()