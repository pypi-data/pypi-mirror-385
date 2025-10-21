import asyncio
import pytest
from market_data_pipeline.orchestration.dag import Dag, Node, DagRuntime, ChannelClosed


async def src_node(_in, out):
    # push 10 ints then close
    for i in range(10):
        for ch in out.values():
            await ch.put(i)
    for ch in out.values():
        await ch.close()


async def double_node(_in, out):
    # read from all inputs, double, forward
    ins = list(_in.values())
    dst = list(out.values())[0]
    try:
        while True:
            x = await ins[0].get()
            await dst.put(x * 2)
    except ChannelClosed:
        await dst.close()


async def sink_node(_in, _out):
    ins = list(_in.values())[0]
    total = 0
    try:
        while True:
            v = await ins.get()
            total += v
    except ChannelClosed:
        # store result as attribute for assertion
        sink_node.result = total  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_dag_runtime_linear():
    dag = Dag()
    dag.add_node(Node("src", src_node))
    dag.add_node(Node("dbl", double_node))
    dag.add_node(Node("snk", sink_node))
    dag.add_edge("src", "dbl")
    dag.add_edge("dbl", "snk")
    rt = DagRuntime(dag)
    stats = await rt.start()
    assert stats.tasks_started == 3
    assert hasattr(sink_node, "result")
    # sum of double(0..9) = 2 * sum 0..9 = 2 * 45 = 90
    assert sink_node.result == 90  # type: ignore[attr-defined]

