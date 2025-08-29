import argparse
import asyncio
import datetime
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import aiofiles
from environs import Env

logger = logging.getLogger(__name__)


@asynccontextmanager
async def managed_connection(host, port):
    reader, writer = await asyncio.open_connection(host, port)
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()


async def read_chat(host, port, folder_path):
    while True:
        try:
            async with managed_connection(host, port) as (reader, writer):
                while message := await reader.readline():
                    await save_message(message, folder_path)
                    await asyncio.sleep(1)
                break  
        except ConnectionError as e:
            logger.error(f"Сетевая ошибка: {e}")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            await asyncio.sleep(5)


async def save_message(message, folder_path):
    folder = Path(__file__).parent / folder_path
    folder.mkdir(exist_ok=True)
    file_path = folder / "data.txt"
    formatted_date = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    message = f"[{formatted_date}] {message.decode()}"
    async with aiofiles.open(file_path, "a", encoding="utf-8") as file:
        await file.write(message)

    print(message, end="")


def create_parser():
    parser = argparse.ArgumentParser(description="Загрузка истории переписки из чата")
    parser.add_argument("--host", default="minechat.dvmn.org", help="host сервера")
    parser.add_argument("--port", default=5000, help="port сервера")
    parser.add_argument("--history", default="minechat", help="Путь к файлу с историей переписки")

    return parser


async def main():
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    env = Env()
    env.read_env()

    parser = create_parser()
    args = parser.parse_args()
    host = args.host or env.str("HOST")
    port = args.port or env.int("READ_PORT")
    history = args.history or env.str("HISTORY")

    await read_chat(host, port, history)


if __name__ == "__main__":
    asyncio.run(main())