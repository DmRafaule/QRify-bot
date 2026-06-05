import io
import sys
import logging
import asyncio

import qrcode
from qrcode.constants import ERROR_CORRECT_L

import cv2
import numpy as np
from qreader import QReader
from PIL import Image

from aiogram import Dispatcher, Bot, F
from aiogram.types import Message, BufferedInputFile, InlineQuery, InlineQueryResultPhoto
from aiogram.filters import Command

from urllib.parse import quote

bot_dispatcher = Dispatcher()
qreader = QReader()
with open(".env", "r") as file:
    buffer = file.read()
    line_pos = buffer.find("BOT_TOKEN")
    TOKEN = buffer[buffer.find("=", line_pos) + 1:buffer.find("\n", line_pos)]

# Convert a text into QR code image and send it back to user
@bot_dispatcher.message(F.text)
async def text2qr(message: Message):
    qr = qrcode.QRCode(
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

# Convert a text into QR code image and send it back to user, inline mode
@bot_dispatcher.inline_query()
async def inlineText2qr(inline_query: InlineQuery):
    query_text = inline_query.query.strip()
    if not query_text:
        await inline_query.answer([], cache_time=1)
        return

    encoded_text = quote(query_text)
    qr_url = f"https://quickchart.io/qr?text={encoded_text}&size=300x300&margin=2"
    result = InlineQueryResultPhoto(
        id=query_text[:64],
        photo_url=qr_url,
        thumbnail_url=qr_url,
        photo_width=300,
        photo_height=300,
        title=f"QR: {query_text[:30]}",
        description=f"Сгенерировать QR для «{query_text[:50]}»"
    )
    await inline_query.answer([result], cache_time=10)

# Convert a QR code into text and send it back to user
@bot_dispatcher.message(F.photo)
async def qr2text(message: Message):
    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)
    downloaded = await message.bot.download_file(file_info.file_path)
    # Конвертируем байты в изображение OpenCV (numpy array)
    image_bytes = downloaded.read()
    pil_image = Image.open(io.BytesIO(image_bytes))
    opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # Распознаём QR-код
    decoded_text = qreader.detect_and_decode(image=opencv_image)

    if decoded_text and decoded_text[0] is not None:
        text = decoded_text[0]
        await message.answer(f"QR:")
        await message.answer(f"{text}")
    else:
        await message.answer("Not recognizable")

async def main() -> None:
    bot = Bot(TOKEN)
    await bot_dispatcher.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())