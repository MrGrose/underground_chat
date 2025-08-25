import asyncio
import datetime
import logging
from pathlib import Path

import aiofiles
import configargparse

logger = logging.getLogger(__name__)


async def read_chat(host, port, folder_path):
    while True:
        try:
            reader, writer = await asyncio.open_connection(host, port)
            while line_bytes := await reader.readline():
                await write_chat_to_file(line_bytes, folder_path)
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


async def write_chat_to_file(line_bytes, folder_path):
    folder = Path(__file__).parent / folder_path
    folder.mkdir(exist_ok=True)
    file_path = folder / "data.txt"
    formatted_date = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    message = f"[{formatted_date}] {line_bytes.decode()}"
    async with aiofiles.open(file_path, "a", encoding="utf-8") as file:
        await file.write(message)

    print(message, end="")


def create_parser():
    parser = configargparse.ArgParser(default_config_files=["config.ini"], description="Загрузка истории переписки из чата")
    parser.add("-c", "--config", is_config_file=True, help="Путь к конфиг. файлу")
    parser.add("--host", env_var="HOST", default="minechat.dvmn.org", help="host сервера")
    parser.add("--port", env_var="PORT", type=int, default=5000, help="port сервера")
    parser.add("--history", env_var="HISTORY", default="minechat", help="Путь к файлу с историей переписки")

    return parser


async def main():
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    parser = create_parser()
    args = parser.parse_args()

    history_path = Path(args.history)
    if not history_path.is_dir():
        history_path.mkdir(parents=True, exist_ok=True)

    await read_chat(args.host, args.port, args.history)


if __name__ == "__main__":
    asyncio.run(main())
