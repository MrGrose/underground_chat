import asyncio
import configparser
import json
import logging

import configargparse
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


async def registration(host, port, nickname):

    reader, writer = await asyncio.open_connection(host, port)
    try:
        data = await reader.readline()
        logger.debug(data.decode().strip())

        writer.write(b"\n")
        await writer.drain()

        data = await reader.readline()
        logger.debug(data.decode().strip())

        if nickname:
            writer.write(nickname.encode().strip() + b"\n")
            await writer.drain()

        writer.write(b"\n")
        await writer.drain()

        data = await reader.readline()
        logger.debug(data.decode().strip())

    finally:
        writer.close()
        await writer.wait_closed()

    return json.loads(data.decode().strip())


async def authorise(host, port, account_hash):
    reader, writer = await asyncio.open_connection(host, port)
    try:
        data = await reader.readline()
        logger.debug(data.decode().strip())

        writer.write(account_hash.encode() + b"\n")
        await writer.drain()

        data = await reader.readline()
        logger.debug(data.decode().strip())

        if json.loads(data.decode()) is None:
            print("Неизвестный токен. Проверьте его или зарегистрируйте заново.")
            return False

        return True
    finally:
        writer.close()
        await writer.wait_closed()


async def submit_message(host, port, account_hash, message):
    reader, writer = await asyncio.open_connection(host, port)
    try:
        data = await reader.readline()
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
    parser.add("--nickname", env_var="USER_NAME", help="nickname пользователя")
    parser.add("-m", default="Я снова тестирую чатик. Раз-два-три.", help="сообщение в чат")
    return parser


def update_config(account_hash, nickname, filename="config_write.ini"):
    config = configparser.ConfigParser()
    config.read(filename)
    config.set("WRITE", "hash", account_hash)
    config.set("WRITE", "nickname", nickname)
    with open(filename, "w") as configfile:
        config.write(configfile)


async def main():
    logging.basicConfig(filename="write_chat.log", format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG)
    load_dotenv(".env")
    parser = create_parser()
    args = parser.parse_args()

    if not args.hash:
        account_hash = await registration(args.host, args.port, args.nickname)
        update_config(account_hash["account_hash"], account_hash["nickname"])
        args = parser.parse_args()
        await submit_message(args.host, args.port, args.hash, args.m)

    is_authorized = await authorise(args.host, args.port, args.hash)

    if not is_authorized:
        account_hash_data = await registration(args.host, args.port, args.nickname)
        update_config(account_hash_data["account_hash"], account_hash_data["nickname"])
        args = parser.parse_args()

    await submit_message(args.host, args.port, args.hash, args.m)


if __name__ == "__main__":
    asyncio.run(main())
