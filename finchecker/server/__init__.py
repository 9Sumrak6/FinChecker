import asyncio


async def send_file(writer, uid, file):
    writer.write(f"beg file {uid}\n".encode())
    await writer.drain()

    f = open(file, "rb")
    await asyncio.sleep(0.01)

    while data := f.read():
        writer.write(f"{uid} {len(data) // 1024 + (len(data) % 1024 > 0)} ".encode() + data)
        await writer.drain()

    await asyncio.sleep(0.1)

    writer.write(f"end file {uid}\n".encode())
    await writer.drain()

    f.close()


clients_names = set()
clients_conns = dict()
clients_locales = dict()


async def chat(reader, writer):
    global clients_names, clients_conns, clients_locales

    me = "{}:{}".format(*writer.get_extra_info('peername'))

    name = await reader.readline()
    name = name.decode()[:-1]

    while name in clients_names:
        writer.write("off".encode())
        await writer.drain()

        name = await reader.readline()
        name = name.decode()[:-1]

    clients_names.add(name)

    writer.write("in".encode())
    await writer.drain()

    clients_conns[name] = asyncio.Queue()

    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(clients_conns[name].get())

    while not reader.at_eof():
        done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)

        for q in done:
            if q is send:
                query = q.result().decode().strip().split()
                print(query)

                if len(query) == 0:
                    writer.write("Command is incorrect.\n".encode())
                    continue
                elif query[0] == 'corr':
                    pass
                elif query[0] == 'stock':
                    pass
                elif query[0] == 'dividends':
                    pass
                elif query[0] == 'balance':
                    pass
                elif query[0] == 'cash':
                    pass
                elif query[0] == 'recom':
                    pass
                elif query[0] == 'sust':
                    pass
                elif query[0] == 'm_hold':
                    pass
                elif query[0] == 'i_hold':
                    pass
                elif query[0] == 'graphics':
                    await send_file(writer, 0, "1.txt")
                elif query[0] == 'sayall':
                    for i in clients_names:
                        if i == name:
                            continue

                        await clients_conns[i].put('say ' + " ".join(query[1:]))
                elif query[0] == 'EOF':
                    send.cancel()
                    receive.cancel()
                    writer.close()

                    clients_names.remove(name)

                    return
                else:
                    print("skip")

                send = asyncio.create_task(reader.readline())
            elif q is receive:
                receive = asyncio.create_task(clients_conns[name].get())
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