import pytest
from market_data_pipeline.orchestration.dag.graph import Dag, Node, DagValidationError


async def noop_node(_in, _out):
    return None


def test_graph_validates_simple_line():
    dag = Dag()
    dag.add_node(Node("src", noop_node))
    dag.add_node(Node("op", noop_node))
    dag.add_node(Node("snk", noop_node))
    dag.add_edge("src", "op")
    dag.add_edge("op", "snk")
    dag.validate()  # should not raise


def test_graph_rejects_cycle():
    dag = Dag()
    dag.add_node(Node("a", noop_node))
    dag.add_node(Node("b", noop_node))
    dag.add_edge("a", "b")
    dag.add_edge("b", "a")
    with pytest.raises(DagValidationError):
        dag.validate()


def test_graph_requires_nodes():
    dag = Dag()
    with pytest.raises(DagValidationError):
        dag.validate()

