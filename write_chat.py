import asyncio
import logging

import configargparse

logger = logging.getLogger(__name__)


async def wtire_chat(host, port, account_hash):
    reader, writer = await asyncio.open_connection(host, port)
    message = "Я снова тестирую чатик. Это третье сообщение."

    writer.write(account_hash.encode() + b"\n")
    await writer.drain()

    for _ in range(3):
        writer.write(message.encode() + b"\n\n")
        await writer.drain()
        await asyncio.sleep(3)
    writer.close()
    await writer.wait_closed()


def create_parser():
    parser = configargparse.ArgParser(default_config_files=["config_write.ini"], description="Отправка сообщений в чат")
    parser.add("-c", "--config", is_config_file=True, help="Путь к конфиг. файлу")
    parser.add("--host", env_var="HOST", help="host сервера")
    parser.add("--port", env_var="WRITE_PORT", help="port сервера")
    parser.add("--hash", env_var="CHAT_TOKEN", help="token пользователя")
    return parser


async def main():
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    parser = create_parser()
    args = parser.parse_args()

    await wtire_chat(args.host, args.port, args.hash)


if __name__ == "__main__":
    asyncio.run(main())
