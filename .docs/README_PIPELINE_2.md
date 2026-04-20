```text
                    ┌──────────────────────┐
                    │   UMLS RRF FILES     │
                    │──────────────────────│
                    │ MRCONSO.RRF          │
                    │ MRDEF.RRF            │
                    │ MRSTY.RRF            │
                    │ MRREL.RRF            │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      POSTGRES        │
                    │──────────────────────│
                    │ MRCONSO              │
                    │ MRDEF                │
                    │ MRSTY                │
                    │ MRREL                │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   PYTHON DB LAYER    │
                    │──────────────────────│
                    │ ConnectDB            │
                    │ Repository methods   │
                    │ SQL files            │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  RAW PYTHON OBJECTS  │
                    │──────────────────────│
                    │ MRCONSO dataclass    │
                    │ MRDEF dataclass      │
                    │ MRSTY dataclass      │
                    │ MRREL dataclass      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ KNOWLEDGE BASE LAYER │
                    │──────────────────────│
                    │ get_concept(cui)     │
                    │ search_candidates()  │
                    │ get_neighbors()      │
                    │ get_definitions()    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ ENTITY LINKING LOGIC │
                    │──────────────────────│
                    │ candidate generation │
                    │ enrichment           │
                    │ ranking              │
                    │ final prediction     │
                    └──────────────────────┘
```