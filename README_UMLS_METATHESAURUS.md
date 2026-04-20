# UMLS Metathesaurus for Entity Linking

This README explains how the **UMLS Metathesaurus** works, how your SQL schema is structured, and how the four imported tables support an **entity linking** pipeline.

---

## 1. What the UMLS Metathesaurus is

The **UMLS Metathesaurus** is a large, multilingual biomedical knowledge base built by the U.S. National Library of Medicine. Its main idea is:

- many source vocabularies exist (SNOMED CT, MeSH, RxNorm, ICD, etc.),
- the same biomedical concept can appear under many names,
- UMLS groups those names under a shared **concept identifier** and records semantic types and relationships.

So, instead of treating every string as a separate entity, UMLS lets you work at the **concept level**.

Example:

- `heart attack`
- `myocardial infarction`
- `MI`

These may all map to the same **CUI** (Concept Unique Identifier), meaning they are alternative names for the same concept.

---

## 2. The basic UMLS data model

Your SQL file uses the UMLS **RRF** (Rich Release Format) and keeps four core files:

1. **MRCONSO** → names, synonyms, identifiers, source vocabularies
2. **MRSTY** → semantic types
3. **MRDEF** → definitions
4. **MRREL** → relations between concepts

This is a very common subset for entity linking because it gives you:

- lexical lookup,
- concept typing,
- optional textual descriptions,
- graph structure between concepts.

---

## 3. The identifiers you need to understand first

### CUI
**Concept Unique Identifier**

This is the most important ID in UMLS. A CUI represents the **meaning** of a concept.

- one concept → one CUI
- many names can point to the same CUI

For entity linking, the final output is often a **CUI**.

### AUI
**Atom Unique Identifier**

An atom is one source-specific occurrence of a term/string.

- same concept can have many AUIs
- same string from different vocabularies can produce different AUIs

Use AUI when you care about the exact source form.

### LUI
**Lexical Unique Identifier**

Groups together terms that are considered the same at the lexical level.

This is more about normalized term identity than concept identity.

### SUI
**String Unique Identifier**

Represents the exact string itself.

### TUI
**Semantic Type Unique Identifier**

Used in **MRSTY** to attach one or more semantic categories to a concept.

Example categories:

- Disease or Syndrome
- Pharmacologic Substance
- Gene or Genome
- Body Part, Organ, or Organ Component

---

## 4. How the four tables work together

### MRCONSO = the lexical entry point
This is usually the **main table for candidate generation**.

It stores:

- the concept (`CUI`)
- the exact term string (`STR`)
- language (`LAT`)
- source vocabulary (`SAB`)
- source term type (`TTY`)
- atom/string/term identifiers (`AUI`, `SUI`, `LUI`)

When you search text such as:

> "patient has myocardial infarction"

You usually search **MRCONSO.STR** first, either with exact match, normalized match, trigram similarity, or full-text search.

Then you retrieve one or more candidate **CUIs**.

### MRSTY = semantic filtering
Once you have candidate CUIs, **MRSTY** tells you what kind of thing each concept is.

Examples:

- if you only want diseases, filter to semantic types like `Disease or Syndrome`
- if you are doing gene linking, filter to gene-related semantic types

This is very useful to reduce ambiguity.

### MRDEF = concept descriptions
**MRDEF** stores textual definitions. Not every concept has one.

This is useful for:

- reranking candidates,
- providing explanations to users,
- creating richer embeddings using concept descriptions.

### MRREL = graph/ontology signal
**MRREL** stores links between concepts or atoms.

This is useful for:

- graph expansion,
- retrieving neighbors,
- relation-aware reranking,
- building knowledge-augmented models.

Important UMLS detail: relationships may appear in both directions, so duplication is expected.

---

## 5. Interpreting your SQL file

Your file is a **custom PostgreSQL import and indexing script** for these four UMLS RRF files.

It does five main things:

1. creates the tables,
2. imports the `.RRF` files with `\copy`,
3. filters some rows,
4. creates indexes for faster search,
5. runs `ANALYZE` so PostgreSQL can optimize queries.

---

## 6. Table-by-table interpretation of your schema

## MRCONSO

### What it represents
Every row in `MRCONSO` is one **atom**: one occurrence of a concept name in one source vocabulary.

This is the central table for text-to-concept lookup.

### Important columns

- `CUI` → concept ID
- `LAT` → language (`ENG`, `POR`, etc.)
- `TS` → term status
- `LUI` → lexical ID
- `STT` → string type
- `SUI` → string ID
- `ISPREF` → whether this atom is preferred for that concept
- `AUI` → atom ID
- `SAUI`, `SCUI`, `SDUI` → source asserted IDs
- `SAB` → source vocabulary abbreviation
- `TTY` → source term type
- `CODE` → useful source code/identifier
- `STR` → the actual text string
- `SRL` → source restriction level
- `SUPPRESS` → suppressibility flag
- `CVF` → content view flag

### How your SQL uses it

Your script:

- loads `MRCONSO.RRF`,
- filters rows by `SUPPRESS`,
- keeps only selected languages,
- creates search indexes.

### Indexes you created

#### `idx_mrconso_cui`
Fast lookup from concept ID to all names.

#### `idx_mrconso_sab`
Fast filtering by source vocabulary.

#### `idx_mrconso_str_trgm`
A trigram GIN index for **fuzzy string matching**.

This is excellent for candidate generation when input text has:

- misspellings,
- punctuation differences,
- small lexical variation.

#### `idx_mrconso_str_fts`
A full-text index using:

```sql
to_tsvector('simple', left(STR, 50000))
```

This allows token-based text search.

#### `idx_mrconso_pref_eng`
A partial index for English preferred concepts:

```sql
WHERE LAT='ENG' AND TS='P'
```

Useful if your pipeline prefers English canonical labels.

### Why MRCONSO matters most in entity linking
Typical use:

1. search `STR`
2. retrieve candidate rows
3. group by `CUI`
4. score/rerank candidates
5. return the best CUI

---

## MRSTY

### What it represents
`MRSTY` assigns one or more **semantic types** to each concept.

A concept can have multiple semantic types.

### Important columns

- `CUI` → concept ID
- `TUI` → semantic type ID
- `STN` → semantic type tree number
- `STY` → semantic type name
- `ATUI` → attribute ID
- `CVF` → content view flag

### Why it matters
This is your main table for **type constraints**.

Examples:

- keep only disease-like concepts,
- remove drugs when you only want procedures,
- use semantic types as model features.

### Indexes you created

- `idx_mrsty_cui`
- `idx_mrsty_tui`
- `idx_mrsty_sty`

These support joins and type-based filters efficiently.

---

## MRDEF

### What it represents
`MRDEF` stores textual **definitions**.

Definitions are attached to atoms/sources, but you will usually access them through the `CUI`.

### Important columns

- `CUI` → concept ID
- `AUI` → atom ID
- `ATUI` → attribute ID
- `SATUI` → source asserted attribute ID
- `SAB` → source vocabulary
- `DEF` → definition text
- `SUPPRESS` → suppressibility flag
- `CVF` → content view flag

### Why it matters
This is useful for:

- explaining linked concepts,
- reranking ambiguous candidates,
- building richer embeddings.

### Indexes you created

- `idx_mrdef_cui`
- `idx_mrdef_def_fts`

So you can both join by concept and search inside definitions.

---

## MRREL

### What it represents
`MRREL` stores relationships between concepts or atoms.

This lets you move from a concept to its related concepts.

### Important columns

- `CUI1`, `CUI2` → concepts in the relation
- `AUI1`, `AUI2` → atoms in the relation
- `STYPE1`, `STYPE2` → what identifier type is being referenced (`CUI`, `AUI`, `CODE`, etc.)
- `REL` → broad relation type
- `RELA` → more specific relation label
- `RUI` → relationship ID
- `SRUI` → source relationship ID
- `SAB` → source vocabulary
- `SL` → source of relationship labels
- `RG` → relation group
- `DIR` → direction flag
- `SUPPRESS` → suppressibility flag
- `CVF` → content view flag

### Why it matters
MRREL is valuable for advanced systems:

- relation-aware retrieval,
- graph neural methods,
- ontology traversal,
- neighbor-based reranking,
- consistency checks.

### Indexes you created

- `idx_mrrel_cui1`
- `idx_mrrel_cui2`
- `idx_mrrel_rel`
- `idx_mrrel_cui1_rel`

These are good for graph traversal queries such as “give me all relations from this concept”.

---

## 7. The SQL import behavior in your script

### `\copy ... DELIMITER '|'`
UMLS RRF files are pipe-delimited.

Your import statements are correct for PostgreSQL command-line loading.

### `NULL ''`
Empty fields are treated as SQL `NULL`.

This is appropriate because many optional UMLS columns are blank.

### `ANALYZE`
The final `ANALYZE` statements are important because PostgreSQL uses them to build query statistics.

Without that, performance can be much worse on large UMLS tables.

---

## 8. Important issue in your filtering logic

Your script currently contains:

```sql
DELETE FROM MRCONSO WHERE SUPPRESS != 'O';
DELETE FROM MRDEF   WHERE SUPPRESS != 'O';
DELETE FROM MRREL   WHERE SUPPRESS != 'O';
```

### What this actually does
It **keeps only rows where `SUPPRESS = 'O'`**.

In UMLS, `O` means **obsolete** content.

So your current script is effectively removing most active content and retaining obsolete rows.

### Why this is probably a problem
For most entity linking systems, you usually want the opposite:

- keep active or usable content,
- drop obsolete/suppressible content.

### Safer alternatives

#### Option A: remove only obsolete rows
```sql
DELETE FROM MRCONSO WHERE SUPPRESS = 'O';
DELETE FROM MRDEF   WHERE SUPPRESS = 'O';
DELETE FROM MRREL   WHERE SUPPRESS = 'O';
```

#### Option B: keep only non-suppressed rows
```sql
DELETE FROM MRCONSO WHERE SUPPRESS != 'N';
DELETE FROM MRDEF   WHERE SUPPRESS != 'N';
DELETE FROM MRREL   WHERE SUPPRESS != 'N';
```

Option A is less aggressive.
Option B is stricter.

For a first entity linking system, **Option A** is usually the safer default.

---

## 9. Your language filter

Your script keeps only these languages:

- ENG, SPA, FRE, GER, ITA, POR, DUT, SWE, NOR, DAN, FIN, POL, CZE, HUN, BAQ, LAV, EST

This means:

- you are creating a multilingual subset,
- but you are discarding all other languages in UMLS.

That is fine if your application only targets those languages.

If your application is Portuguese- or English-first, this reduces storage and speeds up search.

---

## 10. How this schema supports an entity linking pipeline

A practical pipeline with your schema would look like this:

### Step 1: mention detection
Find spans in raw text.

Example:

- input text: `The patient was diagnosed with myocardial infarction.`
- mention: `myocardial infarction`

### Step 2: candidate generation from MRCONSO
Search `MRCONSO.STR` using:

- exact match,
- normalized match,
- trigram similarity,
- full-text search.

This gives candidate rows and candidate CUIs.

### Step 3: candidate consolidation
Group multiple matching rows by `CUI`.

Why? Because many synonyms and many source vocabularies can map to the same concept.

### Step 4: candidate filtering with MRSTY
Join candidates to `MRSTY` and keep only relevant semantic types.

Example:

- if the mention should be a disease, remove candidates typed as organisms, devices, or procedures.

### Step 5: candidate enrichment with MRDEF
Join to `MRDEF` to get definitions for better ranking.

This can help neural rerankers or embedding-based models.

### Step 6: optional graph enrichment with MRREL
Use related concepts as extra context.

Example:

- retrieve parent/child/related disorders,
- use relation neighborhoods as features.

### Step 7: final prediction
Return the best `CUI`, along with:

- canonical label,
- source code,
- semantic type,
- confidence.

---

## 11. Example useful queries

## Get all names for a concept
```sql
SELECT CUI, STR, LAT, SAB, TTY, ISPREF
FROM MRCONSO
WHERE CUI = 'C0027051';
```

## Find candidate concepts by fuzzy string match
```sql
SELECT CUI, STR, SAB, TTY,
       similarity(STR, 'myocardial infarction') AS sim
FROM MRCONSO
WHERE STR % 'myocardial infarction'
ORDER BY sim DESC
LIMIT 20;
```

## Get semantic types for a concept
```sql
SELECT CUI, TUI, STY
FROM MRSTY
WHERE CUI = 'C0027051';
```

## Get definitions for a concept
```sql
SELECT CUI, SAB, DEF
FROM MRDEF
WHERE CUI = 'C0027051';
```

## Get related concepts
```sql
SELECT CUI1, REL, RELA, CUI2, SAB
FROM MRREL
WHERE CUI1 = 'C0027051';
```

## Get a preferred English label for a concept
```sql
SELECT CUI, STR
FROM MRCONSO
WHERE CUI = 'C0027051'
  AND LAT = 'ENG'
  AND TS = 'P'
LIMIT 1;
```

---

## 12. How to think about concept vs term vs string

This distinction is one of the hardest parts of UMLS.

### Concept
The meaning.

Represented by: **CUI**

### Term
A lexical grouping of strings.

Represented by: **LUI**

### String
The literal text form.

Represented by: **SUI**

### Atom
One source-specific occurrence of a term/string.

Represented by: **AUI**

A good mental model is:

- **CUI** = what it means
- **STR/SUI** = how it is written
- **AUI** = where that written form came from in a source vocabulary

---

## 13. Why UMLS can feel confusing at first

Because it is not a simple dictionary.

It is a **metathesaurus**, meaning it merges many vocabularies while preserving source-specific detail.

That creates:

- many synonyms,
- many identifiers,
- duplicated relations,
- multiple semantic types,
- source-specific quirks.

For entity linking, that complexity is useful, but you usually need to **customize** the subset you keep.

---

## 14. Practical recommendations for your project

### Good choices in your script

- keeping only a subset of core tables,
- using PostgreSQL,
- adding trigram and full-text indexes,
- running `ANALYZE`,
- preserving source IDs and semantic types.

### Things I would change first

1. **Fix the `SUPPRESS` filter** so you do not keep only obsolete rows.
2. Consider adding a plain B-tree index on `LAT` if language filtering is frequent.
3. Consider adding a partial index for Portuguese if your project is Portuguese-heavy.
4. Decide on a canonical label rule, for example:
   - English first,
   - preferred atoms first,
   - trusted sources first.
5. If you will rerank with BioBERT/KRISSBERT embeddings, use:
   - `MRCONSO.STR`
   - `MRDEF.DEF`
   - `MRSTY.STY`
   as the main textual fields.

---

## 15. In one sentence per table

- **MRCONSO**: all names and source-specific lexical forms for concepts
- **MRSTY**: what each concept is semantically
- **MRDEF**: textual definitions for concepts/atoms
- **MRREL**: graph edges between concepts or atoms

---

## 16. Final summary

Your SQL file builds a **compact UMLS subset for entity linking**.

The intended logic is:

- `MRCONSO` finds candidate concepts from text,
- `MRSTY` filters them by semantic category,
- `MRDEF` adds descriptive context,
- `MRREL` adds graph knowledge.

That is a solid design for a biomedical entity linking system.

The biggest issue in the current script is the `SUPPRESS` filtering, which appears to retain **obsolete** rows instead of active ones. Fixing that should be your first priority before loading the full Metathesaurus.

---

## 17. Suggested next step

After correcting the `SUPPRESS` logic, the next useful step is to create a small set of helper SQL views such as:

- `preferred_labels`
- `concept_definitions`
- `concept_semantic_types`
- `concept_neighbors`

That makes the database much easier to query from Python.
