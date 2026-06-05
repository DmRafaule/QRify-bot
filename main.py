import io
import sys
import logging
import asyncio
import qrcode
from qrcode.constants import ERROR_CORRECT_L

from aiogram import Dispatcher, Bot, F
from aiogram.types import Message, BufferedInputFile

bot_dispatcher = Dispatcher()
with open(".env", "r") as file:
    buffer = file.read()
    line_pos = buffer.find("BOT_TOKEN")
    TOKEN = buffer[buffer.find("=", line_pos) + 1:buffer.find("\n", line_pos)]


@bot_dispatcher.message(F.text)
async def text2qr(message: Message):
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_L,
    )
    qr.add_data(message.text)
    qr.make(fit=True)
    generated_img = qr.make_image(fill_color="black", back_color="white")

    bytes = io.BytesIO()
    generated_img.save(bytes, 'PNG')
    bytes.seek(0)

    img = BufferedInputFile(
        bytes.getvalue(), 
        filename="qrcode-buffer.png"
    )
    await message.answer(f"QR: '{message.text}'")
    await message.answer_photo(img)

async def main() -> None:
    bot = Bot(TOKEN)
    await bot_dispatcher.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())