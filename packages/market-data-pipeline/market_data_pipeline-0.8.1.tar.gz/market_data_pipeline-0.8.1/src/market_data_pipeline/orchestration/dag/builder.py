from __future__ import annotations

from typing import Any

from loguru import logger

from market_data_pipeline.orchestration.dag.graph import Dag, Edge, Node
from market_data_pipeline.orchestration.dag.registry import ComponentRegistry


class DagBuildError(RuntimeError):
    pass


def build_dag_from_dict(config: dict[str, Any], registry: ComponentRegistry) -> Dag:
    """
    Minimal YAML → Dag builder.

    Expected shape:
    dag:
      nodes:
        - id: src
          type: provider.ibkr.stream
          params:
            stream: "bars"   # or "quotes"
            symbols: ["AAPL", "MSFT"]
            settings: {...}  # provider-specific
        - id: op
          type: operator.buffer
          params:
            max_items: 500
            max_wait_ms: 250
        - id: sink
          type: operator.map
          params:
            # e.g., pass-through or map to sink calls
      edges:
        - [src, op]
        - [op, sink]
    """
    dag_spec = config.get("dag") or {}
    if not dag_spec:
        msg = "Missing 'dag' section in DAG config."
        raise DagBuildError(msg)

    nodes_spec: list[dict[str, Any]] = dag_spec.get("nodes") or []
    edges_spec: list[list[str]] = dag_spec.get("edges") or []

    if not nodes_spec:
        # Allow empty nodes for testing/validation purposes
        logger.warning("No nodes defined under 'dag.nodes' - creating empty DAG")
        return Dag()

    dag = Dag()

    # Create nodes
    for n in nodes_spec:
        nid = n.get("id")
        typ = n.get("type")
        params = n.get("params") or {}

        if not nid or not typ:
            msg = "Each node needs 'id' and 'type'."
            raise DagBuildError(msg)

        # Providers are runtime sources that produce items; operators transform streams.
        # Nothing to instantiate here at graph-time — we hand the registry + params to runtime.
        
        # Create a node function that captures the type and params
        # The runtime will use the registry to instantiate components
        def make_node_fn(node_type: str, node_params: dict):
            async def node_fn(in_ch, out_ch):
                # Placeholder - runtime will use registry to instantiate
                # For now, just log
                from loguru import logger
                logger.debug(f"Node {node_type} called with params {node_params}")
            return node_fn

        node = Node(name=nid, fn=make_node_fn(typ, params))
        dag.add_node(node)

    # Connect edges
    for e in edges_spec:
        if not (isinstance(e, list) and len(e) == 2):
            msg = f"Edge must be [from, to], got: {e}"
            raise DagBuildError(msg)
        src, dst = e
        dag.add_edge(src, dst)

    # Validate DAG
    dag.validate()
    logger.info(f"DAG built with {len(dag.nodes)} nodes and {len(dag.edges)} edges.")
    return dag

