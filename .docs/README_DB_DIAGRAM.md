# UMLS Metathesaurus Table Relationships

This diagram shows how the main UMLS tables in this schema relate to each other.

## Core idea

- `MRCONSO` = concept names / strings / atoms
- `MRSTY` = semantic types for a concept
- `MRDEF` = definitions for a concept
- `MRREL` = relations between concepts
- The main connection key is **`CUI`**

## Diagram

```text
                             ┌────────────────────┐
                             │       MRSTY        │
                             │────────────────────│
                             │ CUI                │
                             │ TUI                │
                             │ STN                │
                             │ STY                │
                             │ ATUI               │
                             │ CVF                │
                             └─────────▲──────────┘
                                       │
                                       │ CUI
                                       │
┌────────────────────┐                 │                 ┌───────────────────────────────┐
│       MRDEF        │                 │                 │            MRREL              │
│────────────────────│                 │                 │───────────────────────────────│
│ CUI                │                 │                 │ CUI1                          │
│ AUI                │                 │                 │ AUI1                          │
│ ATUI               │                 │                 │ STYPE1                        │
│ SATUI              │                 │                 │ REL / RELA                    │
│ SAB                │                 │                 │ CUI2                          │
│ DEF                │                 │                 │ AUI2                          │
│ SUPPRESS           │                 │                 │ STYPE2                        │
│ CVF                │                 │                 │ SAB                           │
└─────────▲──────────┘                 │                 │ SUPPRESS                      │
          │                            │                 └──────▲─────────────────▲──────┘
          │ CUI                        │                        │                 │
          │                            │                        │                 │
          │                            │                      CUI1               CUI2
          │                            │                        │                 │
          │                    ┌───────┴────────────────────────┴─────────────────┴──────┐
          │                    │                        MRCONSO                           │
          │                    │──────────────────────────────────────────────────────────│
          └───────────────────►│ CUI                                                      │◄───────────────────┐
                               │ LAT                                                      │                    │
                               │ TS                                                       │                    │
                               │ LUI                                                      │                    │
                               │ SUI                                                      │                    │
                               │ AUI                                                      │                    │
                               │ SAB                                                      │                    │
                               │ TTY                                                      │                    │
                               │ CODE                                                     │                    │
                               │ STR   (surface form / term text)                         │                    │
                               │ ISPREF                                                   │                    │
                               │ SUPPRESS                                                 │                    │
                               └──────────────────────────────────────────────────────────┘                    │
                                                                                                               │
                                                                                                               │
                                                                                              another concept row
                                                                                                  in MRCONSO
```

## How the tables connect

### 1. `MRCONSO` ↔ `MRSTY`
Join by `CUI`.

This means:
- one concept can have many names in `MRCONSO`
- that same concept can have one or more semantic types in `MRSTY`

### 2. `MRCONSO` ↔ `MRDEF`
Usually join by `CUI`.
Sometimes `AUI` is also useful for more specific atom-level matching.

This means:
- one concept can have multiple definitions
- definitions may come from different source vocabularies (`SAB`)

### 3. `MRCONSO` ↔ `MRREL`
Join `MRCONSO.CUI` to either `MRREL.CUI1` or `MRREL.CUI2`.

This means:
- `MRREL` stores relationships between two concepts
- `CUI1` is the source concept
- `CUI2` is the target concept

## Mental model

```text
MRCONSO = node labels / aliases
MRSTY   = node categories
MRDEF   = node descriptions
MRREL   = edges between nodes
```

## Main join keys

```text
MRCONSO.CUI  <--> MRSTY.CUI
MRCONSO.CUI  <--> MRDEF.CUI
MRCONSO.CUI  <--> MRREL.CUI1
MRCONSO.CUI  <--> MRREL.CUI2
```

Sometimes these are also useful:

```text
MRCONSO.AUI  <--> MRDEF.AUI
MRCONSO.AUI  <--> MRREL.AUI1 / MRREL.AUI2
```

## Identifier meaning

```text
CUI = concept identifier
AUI = atom identifier
LUI = lexical identifier
SUI = string identifier
```

## Entity linking view

A common entity linking flow is:

1. Search user text against `MRCONSO.STR`
2. Retrieve candidate `CUI`s
3. Enrich candidates with:
   - `MRSTY` for semantic type
   - `MRDEF` for definitions
   - `MRREL` for graph neighbors / related concepts

## Short summary

```text
MRCONSO gives the names.
MRSTY gives the types.
MRDEF gives the definitions.
MRREL gives the links between concepts.
Everything mainly connects through CUI.
```
