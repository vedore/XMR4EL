from dataclasses import dataclass, field

@dataclass
class Concept:
    cui: str
    names: list[str] = field(default_factory=list)
    definitions: list[str] = field(default_factory=list)
    semantic_types: list[str] = field(default_factory=list)
    relations: list[dict] = field(default_factory=list)

    def __str__(self) -> str:
            lines = [f"CUI: {self.cui}", ""]

            lines.append("Names:")
            lines.extend([f"  - {x}" for x in self.names] or ["  - None"])
            lines.append("")

            lines.append("Definitions:")
            lines.extend([f"  - {x}" for x in self.definitions] or ["  - None"])
            lines.append("")

            lines.append("Semantic Types:")
            lines.extend([f"  - {x}" for x in self.semantic_types] or ["  - None"])
            lines.append("")

            lines.append("Relations:")
            if self.relations:
                for rel in self.relations:
                    lines.append(
                        f"  - [{rel.get('rel', '?')}/{rel.get('rela', '?')}] "
                        f"{rel.get('target_cui', 'UNKNOWN_CUI')} -> {rel.get('target_name', 'UNKNOWN_NAME')}"
                    )
            else:
                lines.append("  - None")

            return "\n".join(lines)