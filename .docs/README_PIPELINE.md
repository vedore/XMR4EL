# End-to-End Biomedical Entity Linking with UMLS, PostgreSQL, and XMR

This project implements an **end-to-end biomedical entity linking (EL)** pipeline that detects entity mentions in text and links them to **UMLS concepts**.

The system is designed around an **XMR (Extreme Multi-Label Ranking)** view of entity linking: given a mention and its context, the model must rank the correct concept from a **very large label space**. In practice, this means the pipeline combines:

- **mention detection** from raw biomedical text,
- **candidate generation** over UMLS,
- **XMR-based candidate retrieval/ranking**,
- **lexical and rule-based matching**,
- **context-aware re-ranking**, and
- optional **document-level disambiguation**.

The goal is to build a pipeline that is both:

- **research-friendly**, so it can be evaluated and improved module by module, and
- **engineering-friendly**, so it can run on a real UMLS-backed database.

---

## 1. Problem definition

Biomedical entity linking maps a text span such as:

> `diabetes mellitus`

into a normalized identifier in a knowledge base, such as a **UMLS CUI**.

In an **end-to-end** setting, the task includes two subproblems:

1. **Mention Detection / NER**  
   Find the relevant spans in raw text.
2. **Entity Linking / Normalization**  
   Link each span to the correct knowledge base concept.

This project treats entity linking as a **large-scale ranking problem** because the label space is extremely large. UMLS contains many concepts, many aliases, many near-duplicates, and many ambiguous strings. Because of that, the system should not try to directly classify over all possible concepts in a single naive step. Instead, it should use a staged pipeline.

---

## 2. Core idea: EL as XMR

The key design idea is:

> **Entity Linking = Retrieve candidates first, then rank/disambiguate them.**

Under the **XMR** formulation, each mention must be matched against a very large set of possible target labels.

Instead of scoring the full UMLS space online, the system works in two levels:

### Stage A — Candidate Generation
Retrieve a small set of likely concept candidates from UMLS.

### Stage B — Candidate Ranking / Disambiguation
Use context and additional signals to choose the best candidate.

This makes the problem tractable and mirrors how modern large-label EL systems are typically structured.

---

## 3. High-level architecture

```text
Raw biomedical text
    ↓
Sentence/document preprocessing
    ↓
Mention detection (NER / span extraction)
    ↓
Mention normalization
    ↓
Candidate generation over UMLS
    ├── lexical matching
    ├── fuzzy string matching
    ├── abbreviation handling
    └── XMR retrieval / dense retrieval
    ↓
Candidate merging and pruning
    ↓
Candidate re-ranking with local context
    ↓
Optional document-level disambiguation
    ↓
Best UMLS concept (CUI) or NIL
```

---

## 4. Pipeline overview

## 4.1 Text preprocessing

Input documents are normalized before mention detection and linking.

Typical preprocessing includes:

- Unicode normalization
- lowercase normalization where appropriate
- punctuation cleanup
- whitespace cleanup
- sentence splitting
- tokenization
- optional abbreviation detection

This stage should be lightweight. The goal is not to lose biomedical meaning.

---

## 4.2 Mention detection

This module identifies the entity spans that should be linked.

Example:

```text
The patient developed severe vasculitis after treatment.
```

Detected mention:

```text
vasculitis
```

Possible implementation options:

- transformer NER model
- biomedical NER model
- dictionary-assisted mention proposal
- hybrid NER + rules

For the first version of the pipeline, this module can be swapped with:

- gold mentions from a benchmark dataset, or
- a simple NER baseline.

That makes debugging easier while the linking modules are being validated.

---

## 4.3 Mention normalization

Each detected mention is normalized before candidate search.

Example transformations:

- `Vasculitis` → `vasculitis`
- `TNF-alpha` → normalized variant
- whitespace and punctuation normalization
- optional stemming or morphology-aware normalization

The same normalization strategy should also be applied offline to the UMLS alias table.

---

## 4.4 UMLS candidate generation

This is the first major EL stage.

Given a mention, the system retrieves a set of plausible UMLS candidates. This must prioritize **recall**.

### Retrieval signals

The candidate generator should combine multiple signals:

#### 1. Exact lexical match
Fast path for straightforward aliases.

#### 2. Fuzzy lexical match
Useful for spelling variation, morphology, and near-matches.

Examples:

- trigram similarity
- edit distance
- BM25 or text search

#### 3. Abbreviation expansion
Important in biomedical text.

Examples:

- local abbreviation detection from the document
- known abbreviation tables

#### 4. Dense / semantic retrieval
A learned encoder can map mention strings into a retrieval space where semantically related aliases are close.

#### 5. XMR retrieval
Instead of viewing the task as plain nearest-neighbor search only, the system can use an **Extreme Multi-Label Ranking** model to predict the most likely concepts from a very large label space.

### Output of this stage

The output is a **top-k candidate list** per mention.

Example:

```json
[
  {"cui": "C0042384", "name": "Vasculitis", "score": 0.91, "source": "lexical"},
  {"cui": "C0009450", "name": "Congenital Disorder", "score": 0.27, "source": "xmr"}
]
```

A good system should keep enough candidates so the correct answer is rarely dropped early.

---

## 4.5 Candidate merging and pruning

Candidates may come from multiple generators.

The system should:

- merge duplicates by CUI,
- retain provenance for each candidate source,
- preserve lexical and XMR scores,
- optionally filter by semantic type,
- keep only the top-N candidates for the reranker.

This step is critical because UMLS often contains:

- exact alias collisions,
- synonyms shared across multiple concepts,
- highly similar concept names,
- concept ambiguity across semantic types.

---

## 4.6 Candidate re-ranking with context

After candidate retrieval, the system re-ranks the top candidates using local context.

Inputs may include:

- mention string,
- left/right sentence context,
- section title if available,
- candidate preferred term,
- candidate aliases,
- candidate definition,
- candidate semantic types.

This stage resolves ambiguity.

Example:

- mention: `ALS`
- possible meanings:
  - amyotrophic lateral sclerosis
  - advanced life support
  - other domain-specific meanings

The local context determines the correct link.

Possible implementations:

- cross-encoder reranker
- pairwise classifier
- mention-context + candidate encoder
- lightweight neural reranker over candidate features

---

## 4.7 Document-level disambiguation

A mention may be easier to resolve when the rest of the document is considered.

This module can use:

- concept co-occurrence,
- semantic relatedness between predicted concepts,
- graph-based coherence,
- Personalized PageRank (PPR),
- relation-based propagation over candidate graphs.

Example:

If a document already contains concepts strongly related to inflammation or autoimmune disease, then the interpretation of `vasculitic` should become more coherent with `vasculitis` than with an unrelated candidate.

This stage is optional at first, but useful once the retrieval and reranking modules are stable.

---

## 4.8 NIL / abstention handling

Not every mention should be forced to a UMLS concept.

The system should support:

- **NIL prediction**, when no concept is good enough,
- confidence thresholds,
- score calibration.

This avoids incorrect links for:

- out-of-KB mentions,
- overly generic spans,
- annotation mismatches,
- unresolved ambiguity.

---

## 5. Why PostgreSQL is used

PostgreSQL is the backbone of the lexical candidate generation layer.

It is useful for:

- storing UMLS tables,
- indexing aliases and normalized strings,
- exact lookup,
- fuzzy lexical retrieval,
- filtering by source vocabulary and semantic type,
- building reproducible offline preprocessing pipelines.

PostgreSQL is **not** necessarily the only retrieval component, but it is a strong and practical base for the lexical layer.

---

## 6. Suggested UMLS database design

The database should separate concepts from aliases.

### Core tables

#### `concepts`
One row per concept.

Suggested fields:

- `cui`
- `preferred_name`
- `language`
- `source_count`
- `semantic_types`
- `definition`

#### `aliases`
One row per alias / term variant.

Suggested fields:

- `alias_id`
- `cui`
- `alias_text`
- `alias_norm`
- `source_abbreviation`
- `tty`
- `is_preferred`
- `language`

#### `semantic_types`
One row per concept–semantic type relation.

Suggested fields:

- `cui`
- `tui`
- `sty_name`

#### `definitions`
One row per concept definition.

Suggested fields:

- `cui`
- `source`
- `definition_text`

#### `relations`
Optional relation table.

Suggested fields:

- `cui1`
- `rel`
- `rela`
- `cui2`
- `source`

---

## 7. UMLS source files used

A practical starting point is to build from the following UMLS Metathesaurus files:

- **MRCONSO** for names, aliases, and source terms
- **MRSTY** for semantic types
- **MRDEF** for definitions
- **MRREL** for concept relations

A minimal first version can work well with:

- MRCONSO
- MRSTY
- MRDEF

and add MRREL later when graph-based disambiguation is introduced.

---

## 8. Offline vs online pipeline

The system should be split into **offline preparation** and **online inference**.

## 8.1 Offline preparation

This stage runs before inference.

Tasks:

1. import UMLS into PostgreSQL
2. build normalized alias tables
3. compute lexical indexes
4. compute dense embeddings for aliases or concepts
5. build XMR training data
6. train retrieval/ranking models
7. serialize label metadata

## 8.2 Online inference

This stage runs for each document.

Tasks:

1. preprocess document
2. detect mentions
3. normalize mention text
4. retrieve UMLS candidates
5. apply XMR module
6. merge candidate lists
7. rerank using local context
8. optionally apply document-level graph disambiguation
9. return best CUI or NIL

---

## 9. End-to-end flow in detail

```text
Document
  ↓
Preprocessing
  ↓
NER / mention detection
  ↓
Mention normalization
  ↓
Postgres lexical lookup
  ↓
Fuzzy matching / abbreviation handling
  ↓
XMR retrieval
  ↓
Candidate merge
  ↓
Context reranker
  ↓
Document coherence module
  ↓
Final linked concept(s)
```

---

## 10. XMR logic in this project

The **XMR logic** is the central retrieval/ranking idea behind the linker.

Instead of treating UMLS linking as a small-class classification problem, this project treats it as:

- **input**: mention + context
- **label space**: all candidate UMLS concepts
- **task**: rank the correct concept at the top

This is useful because biomedical EL has:

- many thousands or millions of target labels,
- sparse supervision,
- ambiguity,
- many near-duplicate concept names,
- long-tail concepts rarely seen in labelled data.

### What the XMR module should learn

Given a mention, the module should produce:

- top candidate CUIs,
- scores for each candidate,
- embeddings or ranking features useful for reranking.

### Practical role of XMR in the system

The XMR model is not necessarily the entire pipeline.

It is one major module inside the linker.

A practical design is:

- use **lexical retrieval** for high-recall exact/fuzzy matches,
- use **XMR retrieval** for scalable learned ranking,
- combine both before reranking.

This hybrid design is often more robust than using a single module alone.

---

## 11. Suggested training strategy

Because end-to-end EL is complex, development should happen in stages.

### Phase 1 — Gold mention normalization

Ignore mention detection at first.

Use gold spans and focus on:

- candidate generation
- XMR ranking
- reranking

### Phase 2 — Hybrid candidate generation

Add:

- exact matching
- trigram / fuzzy matching
- abbreviation module
- XMR retrieval

### Phase 3 — Context reranking

Train a reranker that uses:

- mention text
- sentence/document context
- candidate concept text
- definitions
- semantic types

### Phase 4 — Document-level disambiguation

Add a graph or coherence module.

### Phase 5 — Full end-to-end EL

Attach the NER / mention detection system and evaluate the full pipeline.

---

## 12. Data strategy

A strong data strategy matters as much as the model.

Possible sources of supervision:

- manually labelled biomedical EL datasets
- distant supervision from linked corpora
- automatically generated weak labels
- synonym-based positive pairs from UMLS
- hard negatives from lexical collisions or nearest neighbors

### Positive training examples

Examples:

- mention ↔ correct CUI
- synonym ↔ concept
- context ↔ linked concept

### Negative training examples

Examples:

- same string but wrong CUI
- near-synonym but different concept
- same semantic family but wrong target
- hard lexical false positives

Hard negatives are especially important for XMR and reranking.

---

## 13. Evaluation plan

Evaluation should be split by module.

### Mention detection

Metrics:

- precision
- recall
- F1

### Candidate generation

Metrics:

- recall@1
- recall@5
- recall@10
- recall@50

This stage measures whether the correct concept appears in the candidate list.

### Candidate ranking

Metrics:

- accuracy@1
- accuracy@k
- MRR

### End-to-end EL

Metrics:

- mention-level exact match
- micro / macro F1
- document-level performance if applicable

### Error analysis

Track failures due to:

- abbreviation ambiguity
- lexical collisions
- semantic type confusion
- missing concepts
- NIL thresholding
- composite mentions
- annotation specificity mismatches

---

## 14. Recommended project structure

```text
project/
├── README.md
├── configs/
│   ├── database.yaml
│   ├── training.yaml
│   └── inference.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   └── cache/
├── sql/
│   ├── schema/
│   ├── import/
│   └── queries/
├── scripts/
│   ├── import_umls.py
│   ├── normalize_aliases.py
│   ├── build_candidates.py
│   ├── train_xmr.py
│   ├── train_reranker.py
│   ├── run_ner.py
│   ├── run_linker.py
│   └── evaluate.py
├── src/
│   ├── db/
│   ├── preprocessing/
│   ├── ner/
│   ├── retrieval/
│   ├── xmr/
│   ├── reranking/
│   ├── graph/
│   ├── inference/
│   └── utils/
├── notebooks/
└── outputs/
```

---

## 15. Example module responsibilities

### `src/preprocessing/`
- text normalization
- tokenization
- sentence segmentation
- abbreviation detection

### `src/ner/`
- mention detection
- span classification
- mention proposal filtering

### `src/retrieval/`
- Postgres lexical retrieval
- fuzzy matching
- semantic type filtering
- alias-based candidate search

### `src/xmr/`
- XMR dataset preparation
- label indexing
- training
- inference
- top-k candidate retrieval

### `src/reranking/`
- mention-candidate pair construction
- neural reranker
- score fusion

### `src/graph/`
- document-level coherence
- PPR or relation-based re-scoring

### `src/inference/`
- orchestrates the full pipeline
- returns final linked concepts

---

## 16. Example inference contract

Input:

```json
{
  "document_id": "doc_001",
  "text": "The patient developed vasculitis after treatment."
}
```

Output:

```json
{
  "document_id": "doc_001",
  "mentions": [
    {
      "text": "vasculitis",
      "start": 22,
      "end": 32,
      "predicted_cui": "C0042384",
      "predicted_name": "Vasculitis",
      "score": 0.97,
      "candidates": [
        {"cui": "C0042384", "score": 0.97},
        {"cui": "C0009450", "score": 0.16}
      ]
    }
  ]
}
```

---

## 17. Design principles

This project follows the following principles:

### 1. Modular first
Each module should be replaceable and independently evaluable.

### 2. Retrieval before full disambiguation
Do not try to solve the full problem in one model pass.

### 3. Hybrid beats fragile
Combine lexical, rule-based, and learned signals.

### 4. Database-backed reproducibility
UMLS preparation and lexical retrieval should be reproducible.

### 5. Candidate recall matters first
If the correct concept is missing from top-k, reranking cannot fix it.

### 6. End-to-end is the final goal, not the first debugging target
Build and validate the linker in stages.

---

## 18. Suggested milestones

### Milestone 1
UMLS imported into PostgreSQL and searchable by alias.

### Milestone 2
Normalized alias retrieval with exact and fuzzy matching.

### Milestone 3
XMR module returns top-k concept candidates.

### Milestone 4
Hybrid candidate merging improves recall@k.

### Milestone 5
Context reranker improves top-1 accuracy.

### Milestone 6
Document-level graph module improves ambiguous cases.

### Milestone 7
NER + linker integrated into a true end-to-end EL pipeline.

---

## 19. Current research hypothesis

The working hypothesis of this project is:

> A hybrid end-to-end biomedical entity linking system that combines PostgreSQL-backed lexical retrieval, XMR-based large-label candidate ranking, and context-aware reranking can outperform lexical-only pipelines and scale better than naive direct classification over UMLS.

---

## 20. Practical first version

A realistic first version of the system should include:

- gold mentions or a basic NER model,
- UMLS stored in PostgreSQL,
- exact and trigram lexical retrieval,
- abbreviation handling,
- XMR-based top-k candidate retrieval,
- simple candidate fusion,
- context reranking,
- optional NIL thresholding.

That version is already strong enough to support experiments, error analysis, and thesis-level evaluation.

---

## 21. Future improvements

Possible future work:

- direct support for multilingual biomedical EL
- graph neural disambiguation over UMLS relations
- semantic type prediction as an auxiliary task
- better NIL calibration
- handling composite mentions
- section-aware context encoding
- active learning for hard examples
- distantly supervised expansion of training data

---

## 22. Summary

This project builds an **end-to-end biomedical entity linking system** over **UMLS**, using **PostgreSQL** for structured concept storage and lexical retrieval, and **XMR logic** for scalable large-label candidate ranking.

The full system is organized as a modular pipeline:

1. detect mentions,
2. normalize mention text,
3. retrieve candidates from UMLS,
4. apply XMR ranking,
5. rerank with context,
6. optionally apply document-level disambiguation,
7. output the best concept or NIL.

The overall philosophy is simple:

> **Use retrieval to make the problem tractable, and use context to make the final decision correct.**

