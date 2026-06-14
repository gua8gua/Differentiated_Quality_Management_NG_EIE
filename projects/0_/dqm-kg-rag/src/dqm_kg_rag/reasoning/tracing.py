from __future__ import annotations

from collections import deque

from dqm_kg_rag.schemas import TracePath, TraceResponse, Triple


def trace_paths(
    outgoing: dict[str, list[Triple]],
    phenomenon: str,
    max_depth: int = 3,
) -> TraceResponse:
    paths: list[TracePath] = []
    actions: set[str] = set()
    queue: deque[tuple[str, list[str], list[str], list[str]]] = deque(
        [(phenomenon, [phenomenon], [], [])]
    )

    while queue:
        current, nodes, relations, evidence = queue.popleft()
        if len(relations) >= max_depth:
            continue

        for triple in outgoing.get(current, []):
            next_nodes = [*nodes, triple.tail]
            next_relations = [*relations, triple.relation]
            next_evidence = [*evidence, triple.description]

            if "处置" in triple.relation or triple.tail_type == "处置措施":
                actions.add(triple.tail)

            paths.append(TracePath(nodes=next_nodes, relations=next_relations, evidence=next_evidence))
            queue.append((triple.tail, next_nodes, next_relations, next_evidence))

    return TraceResponse(
        phenomenon=phenomenon,
        paths=paths,
        recommended_actions=sorted(actions),
    )


def rank_trace_paths(paths: list[TracePath]) -> list[TracePath]:
    return sorted(paths, key=lambda path: (len(path.relations), -len(path.evidence)))

