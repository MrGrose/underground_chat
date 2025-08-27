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
            writer.write(nickname.encode())
            await writer.drain()

        writer.write(b"\n")
        await writer.drain()

        data = await reader.readline()
        logger.debug(f"Регистрация: {data.decode().strip()}")

    finally:
        writer.close()
        await writer.wait_closed()

    return json.loads(data.decode().strip())


async def authorise(host, port, token):
    reader, writer = await asyncio.open_connection(host, port)
    try:
        data = await reader.readline()
        logger.debug(data.decode().strip())

        writer.write(token.encode() + b"\n")
        logger.debug(f"Проверка token: {token}")
        await writer.drain()

        data = await reader.readline()
        logger.debug(f"Полученные данные: {data.decode().strip()}")

        if json.loads(data.decode()) is None:
            print("Неизвестный токен. Проверьте его или зарегистрируйте заново.")
            return False
        return True

    finally:
        writer.close()
        await writer.wait_closed()


async def submit_message(host, port, token, message):
    reader, writer = await asyncio.open_connection(host, port)
    try:
        await reader.readline()
        writer.write(token.encode() + b"\n")
        await writer.drain()

        message_edit = "".join(message).replace("\n", "")
        logger.debug(f"Соообщение: {message_edit}")
        writer.write(message_edit.encode() + b"\n\n")
        await writer.drain()

    finally:
        writer.close()
        await writer.wait_closed()


def create_parser():
    parser = configargparse.ArgParser(default_config_files=["config_write.ini"], description="Отправка сообщений в чат")
    parser.add("-c", "--config", is_config_file=True, help="Путь к конфиг. файлу")
    parser.add("--host", env_var="HOST", help="host сервера")
    parser.add("--port", env_var="WRITE_PORT", help="port сервера")
    parser.add("--token", env_var="USER_TOKEN", help="token пользователя")
    parser.add("--nickname", env_var="USER_NAME", help="nickname пользователя")
    parser.add("-m", default="Я снова тестирую чатик. Раз-два-три.", help="сообщение в чат")
    return parser


def update_config(token, nickname, filename="config_write.ini"):
    config = configparser.ConfigParser()
    config.read(filename)
    config.set("WRITE", "token", token)
    config.set("WRITE", "nickname", nickname)
    with open(filename, "w") as configfile:
        config.write(configfile)


async def main():
    logging.basicConfig(filename="write_chat.log", format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG)
    load_dotenv(".env")
    parser = create_parser()
    args = parser.parse_args()

    if not args.token:
        user_data = await registration(args.host, args.port, args.nickname)
        update_config(user_data["account_hash"], user_data["nickname"])
        args = parser.parse_args()
        await submit_message(args.host, args.port, args.token, args.m)
    else:
        is_authorized = await authorise(args.host, args.port, args.token)
        if not is_authorized:
            account_data = await registration(args.host, args.port, args.nickname)
            update_config(account_data["account_hash"], account_data["nickname"])
            args = parser.parse_args()

        await submit_message(args.host, args.port, args.token, args.m)


if __name__ == "__main__":
    asyncio.run(main())
