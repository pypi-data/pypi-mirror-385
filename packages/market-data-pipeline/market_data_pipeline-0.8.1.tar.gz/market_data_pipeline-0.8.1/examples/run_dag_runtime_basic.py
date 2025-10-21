import asyncio
from market_data_pipeline.orchestration.dag import Dag, Node, DagRuntime, map_async, buffer_async
from market_data_pipeline.orchestration.dag.channel import Channel, ChannelClosed


async def source(_in, out):
    ch = list(out.values())[0]
    for i in range(25):
        await ch.put({"n": i})
    await ch.close()


async def mapper(in_ch, out_ch):
    src = list(in_ch.values())[0]
    dst = list(out_ch.values())[0]
    try:
        while True:
            item = await src.get()
            await dst.put({**item, "n2": item["n"] * 2})
    except ChannelClosed:
        await dst.close()


async def sink(in_ch, _out):
    src = list(in_ch.values())[0]
    try:
        while True:
            batch = await src.get()
            print(f"batch({len(batch)}): {batch[:2]} ...")
    except ChannelClosed:
        pass


async def main():
    dag = Dag()
    dag.add_node(Node("src", source))
    dag.add_node(Node("map", mapper))
    # buffer node using operator adapter
    async def buffer_node(in_ch, out_ch):
        await buffer_async(list(in_ch.values())[0], list(out_ch.values())[0], max_items=5, flush_interval=0.1)

    dag.add_node(Node("buf", buffer_node))
    dag.add_node(Node("snk", sink))

    dag.add_edge("src", "map")
    dag.add_edge("map", "buf")
    dag.add_edge("buf", "snk")

    rt = DagRuntime(dag)
    await rt.start()


if __name__ == "__main__":
    asyncio.run(main())

