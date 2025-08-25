import asyncio
import datetime
import logging

import aiofiles

logger = logging.getLogger(__name__)


async def read_chat(host, port):
    while True:
        try:
            reader, writer = await asyncio.open_connection(host, port)
            while line_bytes := await reader.readline():
                await write_chat_to_file(line_bytes)
                await asyncio.sleep(1)
            writer.close()
            await writer.wait_closed()
            break
        except ConnectionError as e:
            logger.error(f"Сетевая ошибка: {e}")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            await asyncio.sleep(5)


async def write_chat_to_file(line_bytes):
    formatted_date = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    message = f"[{formatted_date}] {line_bytes.decode()}"
    async with aiofiles.open("data.txt", "a", encoding="utf-8") as file:
        await file.write(message)

    print(message, end="")


async def main():
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    host = "minechat.dvmn.org"
    port = 5000
    await read_chat(host, port)


if __name__ == "__main__":
    asyncio.run(main())
