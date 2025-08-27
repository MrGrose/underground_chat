import argparse
import asyncio
import aiofiles
import json
import logging


from environs import Env

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

        async with aiofiles.open("user_auth.txt", "w") as file:
            await file.write(data.decode().strip())

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
    parser = argparse.ArgumentParser(description="Отправка сообщений в чат")
    parser.add_argument("--host", default="minechat.dvmn.org", help="host сервера")
    parser.add_argument("--port", default=5050, help="port сервера")
    parser.add_argument("--token", help="token пользователя")
    parser.add_argument("--nickname", help="nickname пользователя")
    parser.add_argument("-m", help="сообщение в чат")
    return parser


async def main():
    logging.basicConfig(filename="chat.log", format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG)
    env = Env()
    env.read_env()

    parser = create_parser()
    args = parser.parse_args()

    host = args.host or env.str("HOST")
    port = args.port or env.int("SEND_PORT")
    nickname = args.nickname or env.str("USER_NAME", None)
    token = args.token or env.str("USER_TOKEN", None)
    try:
        if not args.m:
            print("Текст сообщение не передан")
            return

        if not token:
            user_data = await registration(host, port, nickname)
            await submit_message(host, port, user_data["account_hash"], args.m)

        else:
            if not await authorise(host, port, token):
                await registration(host, port, nickname)

            await submit_message(host, port, token, args.m)

    except OSError as e:
        logger.error(f"Ошибка соединения: {e}")
    except ConnectionRefusedError:
        logger.error("Соединение отклонено")
    except Exception as e:
        logger.error(f"Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
