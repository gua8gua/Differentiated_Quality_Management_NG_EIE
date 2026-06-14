from __future__ import annotations

import csv
from pathlib import Path

from dqm_kg_rag.schemas import Triple


REQUIRED_COLUMNS = {"head", "relation", "tail"}


def load_triples_from_csv(path: Path) -> list[Triple]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"Triple CSV missing required columns: {sorted(missing)}")
        return [Triple(**row) for row in reader]


def validate_triples(triples: list[Triple]) -> dict[str, object]:
    entities = {triple.head for triple in triples} | {triple.tail for triple in triples}
    relations = {triple.relation for triple in triples}
    empty_descriptions = sum(1 for triple in triples if not triple.description)

    return {
        "triple_count": len(triples),
        "entity_count": len(entities),
        "relation_count": len(relations),
        "empty_description_count": empty_descriptions,
    }

