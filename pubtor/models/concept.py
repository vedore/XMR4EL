from dataclasses import dataclass, field

@dataclass
class Concept:
    cui: str
    names: list[str] = field(default_factory=list)
    definitions: list[str] = field(default_factory=list)
    semantic_types: list[str] = field(default_factory=list)
    relations: list[dict] = field(default_factory=list)