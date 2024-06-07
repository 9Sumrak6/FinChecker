import asyncio


async def chat(reader, writer):
    """
    Check correctness of clients commands and executes them.

    :param reader: read data from IO stream
    :param writer: write data to IO stream
    """

    me = "{}:{}".format(*writer.get_extra_info('peername'))
    print(me)

    print(f'{me} Done')

    receive.cancel()
    writer.close()


async def run_server():
    """Run async server."""
    server = await asyncio.start_server(chat, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
	asyncio.run(run_server())