import asyncio


async def read_chat():
    reader, writer = await asyncio.open_connection(
        "minechat.dvmn.org", 5000)

    while data := await reader.read(522288):
        print(data.decode())


asyncio.run(read_chat())