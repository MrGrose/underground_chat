import asyncio
import logging

import configargparse

logger = logging.getLogger(__name__)


async def write_chat(host, port, account_hash, message):
    reader, writer = await asyncio.open_connection(host, port)

    try:
        data = await reader.read(150)
        logger.debug(data.decode().strip())

        logger.debug(f"user account_hash: {account_hash}")
        writer.write(account_hash.encode() + b"\n")
        await writer.drain()

        data = await reader.readline()
        logger.debug(data.decode().strip())

        logger.debug(f"user message: {message}")
        writer.write(message.encode() + b"\n\n")
        await writer.drain()

    finally:
        writer.close()
        await writer.wait_closed()


def create_parser():
    parser = configargparse.ArgParser(default_config_files=["config_write.ini"], description="Отправка сообщений в чат")
    parser.add("-c", "--config", is_config_file=True, help="Путь к конфиг. файлу")
    parser.add("--host", env_var="HOST", help="host сервера")
    parser.add("--port", env_var="WRITE_PORT", help="port сервера")
    parser.add("--hash", env_var="USER_TOKEN", help="token пользователя")
    parser.add("-m", default="Я снова тестирую чатик. Раз-два-три.", help="сообщение")
    return parser


async def main():
    logging.basicConfig(filename="write_chat.log", format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG)
    parser = create_parser()
    args = parser.parse_args()

    await write_chat(args.host, args.port, args.hash, args.m)


if __name__ == "__main__":
    asyncio.run(main())
