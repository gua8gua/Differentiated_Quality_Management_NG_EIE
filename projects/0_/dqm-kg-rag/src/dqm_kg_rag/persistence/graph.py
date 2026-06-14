from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dqm_kg_rag.ontology.catalog import ENTITY_TYPES, RELATION_TYPES
from dqm_kg_rag.schemas import TracePath, TraceResponse, Triple

CONSTRAINTS = (
    "CREATE CONSTRAINT quality_entity_key IF NOT EXISTS "
    "FOR (n:QualityEntity) REQUIRE (n.name, n.type) IS UNIQUE",
    "CREATE CONSTRAINT quality_entity_type_name IF NOT EXISTS "
    "FOR (n:EntityType) REQUIRE n.name IS UNIQUE",
    "CREATE CONSTRAINT quality_relation_type_name IF NOT EXISTS "
    "FOR (n:RelationType) REQUIRE n.name IS UNIQUE",
)


@dataclass(frozen=True)
class Neo4jConfig:
    uri: str = "bolt://localhost:7687"
    username: str = "neo4j"
    password: str = "password"
    database: str = "neo4j"


def _driver(config: Neo4jConfig) -> Any:
    try:
        from neo4j import GraphDatabase
    except ImportError as exc:
        raise RuntimeError("Neo4j driver is not installed. Run: pip install neo4j") from exc
    return GraphDatabase.driver(config.uri, auth=(config.username, config.password))


def create_constraints(config: Neo4jConfig) -> None:
    with _driver(config) as driver:
        with driver.session(database=config.database) as session:
            for statement in CONSTRAINTS:
                session.run(statement)


def seed_ontology(config: Neo4jConfig) -> None:
    with _driver(config) as driver:
        with driver.session(database=config.database) as session:
            for entity_type in ENTITY_TYPES:
                session.run(
                    """
                    MERGE (t:EntityType {name: $name})
                    SET t.description = $description,
                        t.examples = $examples
                    """,
                    name=entity_type.name,
                    description=entity_type.description,
                    examples=list(entity_type.examples),
                )
            for relation_type in RELATION_TYPES:
                session.run(
                    """
                    MERGE (r:RelationType {name: $name})
                    SET r.description = $description,
                        r.direction = $direction
                    """,
                    name=relation_type.name,
                    description=relation_type.description,
                    direction=relation_type.direction,
                )


def insert_triples(config: Neo4jConfig, triples: list[Triple], source: str = "seed_csv") -> dict[str, int]:
    create_constraints(config)
    seed_ontology(config)

    with _driver(config) as driver:
        with driver.session(database=config.database) as session:
            for triple in triples:
                session.run(
                    """
                    MERGE (h:QualityEntity {name: $head, type: $head_type})
                    SET h.updated_at = datetime()
                    MERGE (t:QualityEntity {name: $tail, type: $tail_type})
                    SET t.updated_at = datetime()
                    MERGE (h)-[r:QUALITY_RELATION {relation: $relation}]->(t)
                    SET r.description = $description,
                        r.source = $source,
                        r.updated_at = datetime()
                    """,
                    head=triple.head,
                    head_type=triple.head_type,
                    tail=triple.tail,
                    tail_type=triple.tail_type,
                    relation=triple.relation,
                    description=triple.description,
                    source=source,
                )
    return {"triple_count": len(triples)}


def trace_phenomenon(config: Neo4jConfig, phenomenon: str, max_depth: int = 3) -> TraceResponse:
    safe_depth = max(1, min(max_depth, 5))
    statement = f"""
    MATCH p = (start:QualityEntity {{name: $phenomenon}})-[:QUALITY_RELATION*1..{safe_depth}]->(target:QualityEntity)
    RETURN nodes(p) AS nodes, relationships(p) AS rels
    LIMIT 50
    """
    paths: list[TracePath] = []
    actions: set[str] = set()

    with _driver(config) as driver:
        with driver.session(database=config.database) as session:
            for record in session.run(statement, phenomenon=phenomenon):
                nodes = [node.get("name", "") for node in record["nodes"]]
                relations = [rel.get("relation", "") for rel in record["rels"]]
                evidence = [rel.get("description", "") for rel in record["rels"]]
                if nodes and nodes[-1] and any("处置" in relation for relation in relations):
                    actions.add(nodes[-1])
                paths.append(TracePath(nodes=nodes, relations=relations, evidence=evidence))

    return TraceResponse(
        phenomenon=phenomenon,
        paths=paths,
        recommended_actions=sorted(actions),
    )

