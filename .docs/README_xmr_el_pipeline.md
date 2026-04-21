# UMLS Entity Linking + XMR Pipeline

This README describes how to join an **Entity Linking (EL)** pipeline with an **eXtreme Multi-label Ranking (XMR/XML)** pipeline for a UMLS-based biomedical concept linking system.

---

## 1. Goal

The goal is to link a mention in text, such as:

```text
"aspirin"
```

to the correct **UMLS concept (CUI)**.

In this setup:

- **Entity Linking** is responsible for:
  - detecting mentions
  - retrieving candidate concepts
  - building enriched concept representations

- **XMR** is responsible for:
  - ranking candidate concepts as labels
  - selecting the best final CUI given the context

So the system is best modeled as:

```text
Text -> Mention Detection -> Candidate Retrieval -> Candidate Enrichment -> XMR Ranking -> Final CUI
```

---

## 2. High-level idea

The cleanest way to join the pipelines is:

- use the **EL pipeline for candidate generation**
- use the **XMR pipeline for candidate ranking**

That means:

1. given a mention, retrieve a set of plausible UMLS CUIs
2. enrich those CUIs with names, definitions, semantic types, and relations
3. pass those candidates to an XMR-style ranker
4. predict the best concept

This avoids asking the XMR model to rank against the entire UMLS label space from scratch on every query.

---

## 3. Why this makes sense

UMLS is very large and highly ambiguous.

For example, a mention can have:

- multiple aliases
- multiple CUIs with similar strings
- missing or noisy context

If you directly rank over every possible UMLS CUI, training and inference become very expensive.

A two-stage architecture is much more practical:

### Stage 1: Candidate Generation
Retrieve a manageable set of possible CUIs.

### Stage 2: Candidate Ranking
Use a stronger model to choose the correct one.

This is the same general idea used in many modern retrieval + reranking systems.

---

## 4. Complete pipeline

## 4.1 Mention Detection

Input text:

```text
The patient was treated with aspirin for chest pain.
```

Possible detected mentions:

- `aspirin`
- `chest pain`

This component can be:

- rule-based
- dictionary-based
- NER model-based
- transformer-based span detector

At the end of this stage, each mention should have:

- mention text
- start offset
- end offset
- local context
- document context

---

## 4.2 Candidate Retrieval

This is where the **EL pipeline** begins narrowing the space.

For a mention like `aspirin`, retrieve candidate CUIs using one or more of these strategies:

### Lexical retrieval from `MRCONSO`

Examples:

- exact match
- lowercase normalized match
- punctuation-normalized match
- trigram/fuzzy match

### Embedding retrieval

Build embeddings for UMLS aliases or concept text and retrieve nearest neighbors with **FAISS**.

### Hybrid retrieval

Union of:

- lexical candidates
- embedding candidates

This usually gives better recall.

The output of this stage is something like:

```text
mention -> [candidate_cui_1, candidate_cui_2, ..., candidate_cui_k]
```

---

## 4.3 Candidate Enrichment

Once candidate CUIs are retrieved, enrich each candidate using the repository layer backed by PostgreSQL.

For each CUI, retrieve:

- **names** from `MRCONSO`
- **definitions** from `MRDEF`
- **semantic types** from `MRSTY`
- **relations** from `MRREL`

That gives a richer concept object that is much more useful for ranking.

Example Python dataclass:

```python
from dataclasses import dataclass, field

@dataclass
class Concept:
    cui: str
    names: list[str] = field(default_factory=list)
    definitions: list[str] = field(default_factory=list)
    semantic_types: list[str] = field(default_factory=list)
    relations: list[dict] = field(default_factory=list)
```

At this stage, candidate retrieval has become a **candidate set construction** step.

---

## 4.4 XMR Ranking

This is where the **XMR pipeline** enters.

Each retrieved CUI is treated as a candidate label.

The model receives:

- the mention text
- left/right or sentence context
- optionally document context
- the candidate concept representation

The model then scores each candidate CUI.

A candidate concept representation can be built from:

```text
name [SEP] definition [SEP] semantic types
```

Example:

```text
aspirin [SEP] A salicylate drug used to reduce pain... [SEP] Pharmacologic Substance
```

The XMR model then learns a scoring function like:

```text
score(mention_context, candidate_concept)
```

The highest-scoring candidate becomes the final linked CUI.

---

## 5. Best practical architecture

The best starting architecture for this project is:

```text
Mention -> Candidate Retrieval -> Candidate Aggregation -> Candidate Enrichment -> XMR Reranker -> Final CUI
```

### More detailed flow

```text
Raw text
  -> mention detector
  -> mention span + mention text + context
  -> lexical retrieval from MRCONSO
  -> embedding retrieval from FAISS
  -> merge and deduplicate candidates by CUI
  -> fetch names/definitions/semantic types/relations from PostgreSQL
  -> create Concept objects
  -> score candidates with XMR model
  -> return top-1 or top-k CUIs
```

---

## 6. Alias-level retrieval vs Concept-level ranking

This is a very important design decision.

### Recommendation

- **Retrieve by alias**
- **Rank by concept (CUI)**

Why?

Because UMLS stores many strings per concept.

If you index aliases from `MRCONSO`, retrieval becomes much stronger because the surface forms are directly searchable.

However, the final prediction target should still be the **concept CUI**, not the alias row.

### So the pipeline becomes:

- FAISS index rows = alias embeddings
- metadata maps alias row -> CUI
- candidates are aggregated by CUI
- XMR ranks the CUI-level candidates

This is usually much better than indexing only one name per concept.

---

## 7. Candidate aggregation

If multiple aliases point to the same CUI, merge them.

For each CUI, you can aggregate signals such as:

- maximum similarity score
- average similarity score
- whether an exact lexical match exists
- whether a preferred term matched
- vocabulary/source weights (`SAB`)

This gives a much stronger candidate representation before ranking.

Example aggregated candidate structure:

```python
from dataclasses import dataclass, field

@dataclass
class RetrievedCandidate:
    cui: str
    alias_hits: list[str] = field(default_factory=list)
    lexical_score: float = 0.0
    embedding_score: float = 0.0
    exact_match: bool = False
    preferred_match: bool = False
```

---

## 8. Suggested intermediate object between EL and XMR

A clean way to connect the pipelines is with an object like this:

```python
from dataclasses import dataclass, field

@dataclass
class MentionCandidateSet:
    mention: str
    span_start: int
    span_end: int
    left_context: str
    right_context: str
    document_context: str
    candidates: list[Concept] = field(default_factory=list)
```

The **EL pipeline produces** this object.

The **XMR pipeline consumes** this object.

This is much better than passing around raw SQL rows.

---

## 9. Role of PostgreSQL and FAISS

## PostgreSQL

PostgreSQL is the structured knowledge layer.

Use it for:

- storing UMLS tables
- lexical lookups
- retrieving concept metadata
- resolving CUIs into rich concept objects

Tables of interest:

- `MRCONSO` for names/aliases
- `MRDEF` for definitions
- `MRSTY` for semantic types
- `MRREL` for relations

## FAISS

FAISS is the dense retrieval layer.

Use it for:

- storing alias embeddings
- nearest-neighbor search over mentions
- fast top-k retrieval

### Recommended setup

- store embeddings as `float32`
- normalize vectors
- use cosine-style retrieval through inner product on normalized vectors
- keep a metadata mapping from FAISS row id -> alias/CUI information

---

## 10. Offline indexing pipeline

This runs before inference.

### Step 1: Extract aliases
From `MRCONSO`, collect rows such as:

- CUI
- STR
- ISPREF
- SAB
- TTY

### Step 2: Normalize strings
Examples:

- lowercase
- strip punctuation
- collapse whitespace

### Step 3: Build alias text representations
You can embed:

- alias only
- alias + semantic type
- alias + definition

A simple baseline is alias only.

### Step 4: Compute embeddings
Use your encoder to transform each alias into a vector.

### Step 5: Save vectors
Store the matrix with NumPy.

### Step 6: Build FAISS index
Create a searchable vector index.

### Step 7: Save metadata
For each vector row, keep metadata such as:

- FAISS row id
- CUI
- alias string
- `ISPREF`
- `SAB`
- maybe `TTY`

---

## 11. Online inference pipeline

At runtime, the full system works like this:

### Step 1: detect mention
Example mention:

```text
aspirin
```

### Step 2: lexical candidate retrieval
Use PostgreSQL `MRCONSO` queries:

- exact match
- normalized match
- fuzzy/trigram match

### Step 3: embedding candidate retrieval
Embed the mention or mention+context and search FAISS.

### Step 4: merge results
Take the union of lexical and vector candidates.

### Step 5: deduplicate by CUI
Because many aliases can map to the same concept.

### Step 6: enrich candidates
Fetch metadata from PostgreSQL.

### Step 7: XMR ranking
Score candidates using the mention context.

### Step 8: output final result
Return:

- top-1 CUI
- or top-k candidates with scores

---

## 12. How XMR fits mathematically

In this project, XMR can be seen as:

- **instance** = mention + context
- **label** = UMLS CUI

This is naturally an extreme classification / ranking problem because the label space is large.

However, instead of ranking across the full UMLS label set every time, the system first narrows the candidate space.

So the practical training/inference view becomes:

```text
mention_context -> retrieve top-k candidate labels -> rank them -> predict best label
```

This keeps the problem tractable while preserving the XMR formulation.

---

## 13. Recommended scoring signals

A strong reranker should combine multiple signals.

Examples:

- lexical match score
- dense retrieval similarity
- preferred-term match
- semantic type compatibility
- definition/context similarity
- graph/relational features from `MRREL`

A simple hybrid score could be:

```text
final_score(cui) =
    0.5 * lexical_score +
    0.3 * embedding_score +
    0.2 * context_score
```

Later, this can be replaced with a learned model.

---

## 14. Hard negatives for training

A useful training strategy is to generate hard negatives from retrieval.

For each gold mention -> CUI pair:

- positive = correct CUI
- negatives = confusing retrieved candidates

Good hard negatives include:

- close lexical matches
- semantically related CUIs
- same semantic type CUIs
- nearest FAISS neighbors that are wrong

This makes the XMR ranker much stronger.

---

## 15. Recommended codebase structure

```text
project/
├── db/
│   └── connection.py
├── repositories/
│   └── umls_repository.py
├── queries/
│   ├── mrconso/
│   ├── mrdef/
│   ├── mrsty/
│   └── mrrel/
├── models/
│   ├── mrconso.py
│   ├── mrdef.py
│   ├── mrsty.py
│   ├── mrrel.py
│   └── concept.py
├── indexing/
│   ├── build_embeddings.py
│   ├── build_faiss_index.py
│   └── metadata.py
├── retrieval/
│   ├── lexical_retriever.py
│   ├── vector_retriever.py
│   └── hybrid_retriever.py
├── ranking/
│   ├── xmr_ranker.py
│   └── features.py
├── pipeline/
│   └── linker.py
└── README.md
```

---

## 16. Repository layer responsibilities

The repository layer should hide SQL details from the rest of the application.

Example responsibilities:

- `get_names_by_cui(cui)`
- `get_definitions_by_cui(cui)`
- `get_semantic_types_by_cui(cui)`
- `get_relations_by_cui(cui)`
- `get_candidate_cuis_exact(mention)`
- `get_candidate_cuis_fuzzy(mention)`

This keeps the XMR and retrieval logic independent from raw SQL.

---

## 17. Minimal end-to-end conceptual flow

```text
Input document
  -> detect mention
  -> retrieve lexical candidates from MRCONSO
  -> retrieve embedding candidates from FAISS
  -> merge + deduplicate by CUI
  -> enrich each CUI with names/definitions/semantic types/relations
  -> convert to Concept objects
  -> score candidates with XMR model
  -> choose best CUI
```

---

## 18. Best first implementation

A strong first version of the system should be:

1. Mention detection
2. Exact lexical retrieval from `MRCONSO`
3. Fallback fuzzy retrieval from `MRCONSO`
4. FAISS retrieval over alias embeddings
5. Merge candidates by CUI
6. Build `Concept` objects from PostgreSQL
7. Rank with a simple learned scorer
8. Later replace the scorer with a stronger XMR model

This gives a practical, modular, and extensible system.

---

## 19. Final summary

The cleanest way to join **Entity Linking** and **XMR** is:

- **EL narrows the search space**
- **XMR performs the final ranking**

So the joined pipeline is:

```text
Mention -> Candidate Retrieval -> Candidate Enrichment -> XMR Ranking -> Final CUI
```

And the best engineering choice is:

- PostgreSQL for structured UMLS access
- FAISS for dense candidate retrieval
- repository classes for concept retrieval
- an intermediate candidate-set object between EL and XMR
- XMR as the final context-aware ranking layer

This structure is scalable, modular, and a strong basis for a biomedical entity linking system.
