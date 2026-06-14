from __future__ import annotations

import sqlite3
from pathlib import Path

from dqm_kg_rag.ontology.catalog import ENTITY_TYPES, RELATION_TYPES
from dqm_kg_rag.schemas import Triple

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS entity_types (
    name TEXT PRIMARY KEY,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS relation_types (
    name TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    direction TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, type),
    FOREIGN KEY(type) REFERENCES entity_types(name)
);

CREATE TABLE IF NOT EXISTS triples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    head_id INTEGER NOT NULL,
    relation TEXT NOT NULL,
    tail_id INTEGER NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT 'seed_csv',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(head_id, relation, tail_id),
    FOREIGN KEY(head_id) REFERENCES entities(id) ON DELETE CASCADE,
    FOREIGN KEY(tail_id) REFERENCES entities(id) ON DELETE CASCADE,
    FOREIGN KEY(relation) REFERENCES relation_types(name)
);

CREATE TABLE IF NOT EXISTS quality_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phenomenon TEXT NOT NULL,
    risk_level TEXT NOT NULL CHECK(risk_level IN ('低', '中', '高')),
    evidence_json TEXT NOT NULL DEFAULT '[]',
    trace_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
CREATE INDEX IF NOT EXISTS idx_triples_head ON triples(head_id);
CREATE INDEX IF NOT EXISTS idx_triples_tail ON triples(tail_id);
CREATE INDEX IF NOT EXISTS idx_triples_relation ON triples(relation);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_schema(db_path: Path) -> None:
    with connect(db_path) as connection:
        connection.executescript(SCHEMA_SQL)
        seed_ontology(connection)


def seed_ontology(connection: sqlite3.Connection) -> None:
    connection.executemany(
        """
        INSERT INTO entity_types(name, description)
        VALUES (?, ?)
        ON CONFLICT(name) DO UPDATE SET description=excluded.description
        """,
        [(item.name, item.description) for item in ENTITY_TYPES],
    )
    connection.executemany(
        """
        INSERT INTO relation_types(name, description, direction)
        VALUES (?, ?, ?)
        ON CONFLICT(name) DO UPDATE
        SET description=excluded.description, direction=excluded.direction
        """,
        [(item.name, item.description, item.direction) for item in RELATION_TYPES],
    )


def _ensure_entity(connection: sqlite3.Connection, name: str, entity_type: str) -> int:
    connection.execute(
        """
        INSERT INTO entities(name, type)
        VALUES (?, ?)
        ON CONFLICT(name, type) DO NOTHING
        """,
        (name, entity_type),
    )
    row = connection.execute(
        "SELECT id FROM entities WHERE name = ? AND type = ?",
        (name, entity_type),
    ).fetchone()
    if row is None:
        raise RuntimeError(f"Failed to insert entity: {name}/{entity_type}")
    return int(row["id"])


def insert_triples(db_path: Path, triples: list[Triple], source: str = "seed_csv") -> dict[str, int]:
    initialize_schema(db_path)
    inserted = 0
    with connect(db_path) as connection:
        for triple in triples:
            head_id = _ensure_entity(connection, triple.head, triple.head_type)
            tail_id = _ensure_entity(connection, triple.tail, triple.tail_type)
            before = connection.total_changes
            connection.execute(
                """
                INSERT INTO triples(head_id, relation, tail_id, description, source)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(head_id, relation, tail_id) DO UPDATE
                SET description=excluded.description, source=excluded.source
                """,
                (head_id, triple.relation, tail_id, triple.description, source),
            )
            if connection.total_changes > before:
                inserted += 1
    return {"triple_count": len(triples), "insert_or_update_count": inserted}


def database_stats(db_path: Path) -> dict[str, int]:
    with connect(db_path) as connection:
        return {
            "entity_type_count": int(connection.execute("SELECT COUNT(*) FROM entity_types").fetchone()[0]),
            "relation_type_count": int(connection.execute("SELECT COUNT(*) FROM relation_types").fetchone()[0]),
            "entity_count": int(connection.execute("SELECT COUNT(*) FROM entities").fetchone()[0]),
            "triple_count": int(connection.execute("SELECT COUNT(*) FROM triples").fetchone()[0]),
            "case_count": int(connection.execute("SELECT COUNT(*) FROM quality_cases").fetchone()[0]),
        }

