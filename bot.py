import os
import openai
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types.input_file import BufferedInputFile
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def generete_image(prompt: str) -> str:
    try:
        response = openai.images.generate(
            prompt=prompt,
            n=1,
            size="256x256"
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        return f"Ошибка при генерации изображения: {e}"

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот, который генерирует изображения с помощью DALL·E. Отправь мне описание, и я сгенерирую картинку для тебя.")

@dp.message()
async def handle_message(message: Message):
    prompt = message.text
    await message.answer("Генерация изображения...")
    
    image_url = await generete_image(prompt)
    if image_url.startswith("Ошибка"):
        await message.answer(image_url)
        return

    try:
        response = requests.get(image_url)
        response.raise_for_status()
    except Exception as e:
        await message.answer(f"Ошибка при загрузке изображения: {e}")
        return

    # Создаем BufferedInputFile из байтов
    image_file = BufferedInputFile(response.content, filename="image.png")
    await message.answer_photo(photo=image_file, caption="Вот ваше изображение:")

async def main():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(e)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
