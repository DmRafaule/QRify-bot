import sys
import logging
import asyncio

from aiogram import Dispatcher, Bot

bot_dispatcher = Dispatcher()
with open(".env", "r") as file:
    buffer = file.read()
    line_pos = buffer.find("BOT_TOKEN")
    TOKEN = buffer[buffer.find("=", line_pos) + 1:buffer.find("\n", line_pos)]

async def main() -> None:
    bot = Bot(TOKEN)
    await bot_dispatcher.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())