from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .importers.csv_importer import load_triples_from_csv, validate_triples
from .reasoning.tracing import trace_paths
from .schemas import TracePath, TraceResponse, Triple


class InMemoryGraph:
    def __init__(self, triples: list[Triple]) -> None:
        self.triples = triples
        self.outgoing: dict[str, list[Triple]] = defaultdict(list)
        for triple in triples:
            self.outgoing[triple.head].append(triple)

    @classmethod
    def from_csv(cls, path: Path) -> "InMemoryGraph":
        return cls(load_triples_from_csv(path))

    def trace(self, phenomenon: str, max_depth: int = 3) -> TraceResponse:
        return trace_paths(self.outgoing, phenomenon, max_depth)

    def as_elements(self) -> dict[str, list[dict[str, str]]]:
        nodes: dict[str, dict[str, str]] = {}
        edges: list[dict[str, str]] = []

        for triple in self.triples:
            nodes.setdefault(triple.head, {"id": triple.head, "label": triple.head, "type": triple.head_type})
            nodes.setdefault(triple.tail, {"id": triple.tail, "label": triple.tail, "type": triple.tail_type})
            edges.append({"source": triple.head, "target": triple.tail, "label": triple.relation})

        return {"nodes": list(nodes.values()), "edges": edges}

    def validate(self) -> dict[str, object]:
        return validate_triples(self.triples)


def default_graph() -> InMemoryGraph:
    root = Path(__file__).resolve().parents[2]
    return InMemoryGraph.from_csv(root / "data" / "seed_triples" / "quality_triples.csv")

