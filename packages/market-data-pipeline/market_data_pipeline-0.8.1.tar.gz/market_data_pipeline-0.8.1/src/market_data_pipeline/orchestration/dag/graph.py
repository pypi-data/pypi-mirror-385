from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


class DagValidationError(ValueError):
    pass


@dataclass(frozen=True)
class Node:
    """A DAG node. `fn` should be an async callable that processes a Channel in → out."""
    name: str
    fn: Callable[..., Any]


@dataclass(frozen=True)
class Edge:
    """Directed edge from `src` → `dst` (by node name)."""
    src: str
    dst: str


@dataclass
class Dag:
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)

    def add_node(self, node: Node) -> None:
        if node.name in self.nodes:
            raise DagValidationError(f"Duplicate node name: {node.name}")
        self.nodes[node.name] = node

    def add_edge(self, src: str, dst: str) -> None:
        if src not in self.nodes:
            raise DagValidationError(f"Edge src missing: {src}")
        if dst not in self.nodes:
            raise DagValidationError(f"Edge dst missing: {dst}")
        self.edges.append(Edge(src, dst))

    def validate(self) -> None:
        """Validates that the graph is a DAG (no cycles) and all nodes are connected (at least 1)."""
        if not self.nodes:
            raise DagValidationError("DAG has no nodes")

        # Build adjacency
        adj: dict[str, list[str]] = {n: [] for n in self.nodes}
        indeg: dict[str, int] = dict.fromkeys(self.nodes, 0)
        for e in self.edges:
            adj[e.src].append(e.dst)
            indeg[e.dst] += 1

        # Kahn's algorithm for cycle detection
        roots = [n for n, d in indeg.items() if d == 0]
        if not roots:
            raise DagValidationError("DAG has no source nodes (no indegree==0)")
        visited: list[str] = []
        stack: list[str] = roots[:]
        while stack:
            u = stack.pop()
            visited.append(u)
            for v in adj[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    stack.append(v)

        if len(visited) != len(self.nodes):
            # Cycle or disconnected in-degree never reached 0
            remaining: set[str] = set(self.nodes).difference(visited)
            raise DagValidationError(f"DAG not acyclic or disconnected; remaining: {sorted(remaining)}")

    def sources(self) -> list[str]:
        indeg: dict[str, int] = dict.fromkeys(self.nodes, 0)
        for e in self.edges:
            indeg[e.dst] += 1
        return [n for n, d in indeg.items() if d == 0]

    def successors(self, name: str) -> list[str]:
        return [e.dst for e in self.edges if e.src == name]

