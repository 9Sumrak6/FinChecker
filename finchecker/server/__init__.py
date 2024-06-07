import asyncio



clients_names = set()
clients_conns = dict()
clients_locales = dict()


async def chat(reader, writer):
    global clients_names, clients_conns, clients_locales

    me = "{}:{}".format(*writer.get_extra_info('peername'))
    print(me)

    name = await reader.readline()
    name = name.decode()[:-1]

    print(name)

    if name in clients_names:
        writer.write("off\n".encode())
        return
    else:
        clients_names.add(name)

        writer.write("in\n".encode())

    clients_conns[name] = asyncio.Queue()

    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(clients_conns[name].get())

    print("OK")

    while not reader.at_eof():
        done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)

        for q in done:
            if q is send:
                query = q.result().decode().strip().split()
                print("----------", query)

                if len(query) == 0:
                    writer.write("Command is incorrect.\n".encode())
                    continue
                elif query[0] == 'pic':
                    pass
                elif query[0] == 'EOF':
                    send.cancel()
                    receive.cancel()
                    writer.close()

                    clients_names.remove(name)

                    return
                else:
                    print("skip")
                send = asyncio.create_task(reader.readline())
            elif q in receive:
                print(1)
                receive = asyncio.create_task(clients_queue[name].get())
                writer.write("{}\n".format(q.result()).encode())
                await writer.drain()

    print(f'{me} Done')

    send.cancel()
    receive.cancel()
    writer.close()

    clients_names.remove(name)


async def run_server():
    """Run async server."""
    server = await asyncio.start_server(chat, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

def main():
	asyncio.run(run_server())