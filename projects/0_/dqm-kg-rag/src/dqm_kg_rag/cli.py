from __future__ import annotations

import argparse
from pathlib import Path

from .importers.csv_importer import load_triples_from_csv
from .persistence.graph import Neo4jConfig, create_constraints, insert_triples as insert_neo4j_triples, trace_phenomenon
from .persistence.relational import database_stats, initialize_schema, insert_triples as insert_sqlite_triples
from .store import default_graph

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TRIPLES = ROOT / "data" / "seed_triples" / "quality_triples.csv"
DEFAULT_SQLITE = ROOT / "data" / "quality_kg.sqlite"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Trace quality risks in the seed knowledge graph.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    trace = subparsers.add_parser("trace", help="Trace a quality phenomenon in the in-memory graph.")
    trace.add_argument("phenomenon", help="Quality phenomenon to trace, e.g. 接收通道噪声升高")
    trace.add_argument("--depth", type=int, default=3)

    init_sqlite = subparsers.add_parser("init-sqlite", help="Create relational schema and constraints.")
    init_sqlite.add_argument("--db", type=Path, default=DEFAULT_SQLITE)

    import_sqlite = subparsers.add_parser("import-sqlite", help="Import triples into SQLite.")
    import_sqlite.add_argument("--db", type=Path, default=DEFAULT_SQLITE)
    import_sqlite.add_argument("--triples", type=Path, default=DEFAULT_TRIPLES)

    sqlite_stats = subparsers.add_parser("sqlite-stats", help="Show SQLite graph statistics.")
    sqlite_stats.add_argument("--db", type=Path, default=DEFAULT_SQLITE)

    neo4j_constraints = subparsers.add_parser("neo4j-constraints", help="Create Neo4j constraints.")
    add_neo4j_args(neo4j_constraints)

    import_neo4j = subparsers.add_parser("import-neo4j", help="Import triples into Neo4j.")
    add_neo4j_args(import_neo4j)
    import_neo4j.add_argument("--triples", type=Path, default=DEFAULT_TRIPLES)

    neo4j_trace = subparsers.add_parser("neo4j-trace", help="Trace a phenomenon in Neo4j.")
    add_neo4j_args(neo4j_trace)
    neo4j_trace.add_argument("phenomenon")
    neo4j_trace.add_argument("--depth", type=int, default=3)
    return parser


def add_neo4j_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--uri", default="bolt://localhost:7687")
    parser.add_argument("--username", default="neo4j")
    parser.add_argument("--password", default="password")
    parser.add_argument("--database", default="neo4j")


def neo4j_config(args: argparse.Namespace) -> Neo4jConfig:
    return Neo4jConfig(
        uri=args.uri,
        username=args.username,
        password=args.password,
        database=args.database,
    )


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "trace":
        response = default_graph().trace(args.phenomenon, args.depth)
        print(response.model_dump_json(indent=2))
    elif args.command == "init-sqlite":
        initialize_schema(args.db)
        print(database_stats(args.db))
    elif args.command == "import-sqlite":
        triples = load_triples_from_csv(args.triples)
        print(insert_sqlite_triples(args.db, triples))
        print(database_stats(args.db))
    elif args.command == "sqlite-stats":
        print(database_stats(args.db))
    elif args.command == "neo4j-constraints":
        create_constraints(neo4j_config(args))
        print({"status": "ok", "action": "neo4j_constraints"})
    elif args.command == "import-neo4j":
        triples = load_triples_from_csv(args.triples)
        print(insert_neo4j_triples(neo4j_config(args), triples))
    elif args.command == "neo4j-trace":
        response = trace_phenomenon(neo4j_config(args), args.phenomenon, args.depth)
        print(response.model_dump_json(indent=2))


if __name__ == "__main__":
    main()

