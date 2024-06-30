import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

import config
from random_fox import fox  # Убедитесь, что у вас есть модуль random_fox с функцией fox
from keyboards import kb1, kb2  # Убедитесь, что у вас есть модуль keyboards с kb1 и kb2

API_TOKEN = config.token
WEATHER_API_KEY = config.weather_api_key
CURRENCY_API_KEY = "your_new_active_api_key"  # замените старый ключ на новый активный

# Включаем логирование, чтобы видеть сообщения в консоли
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_info = {
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"]
        }
        return weather_info
    else:
        return None


def get_exchange_rate(from_currency, to_currency):
    url = f"https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/latest/{from_currency.upper()}"
    response = requests.get(url)
    # Получение более детальной информации для отладки
    logging.info(f"Request URL: {url}")
    logging.info(f"Response Status Code: {response.status_code}")
    logging.info(f"Response: {response.text}")

    if response.status_code == 200:
        data = response.json()
        logging.info(f"Data received: {data}")  # Debug output for the data
        conversion_rates = data.get("conversion_rates", {})
        if not conversion_rates:
            logging.info("No conversion rates found in the response.")
            return None
        if to_currency.upper() in conversion_rates:
            return conversion_rates[to_currency.upper()]
        else:
            logging.info(f"{to_currency.upper()} not found in conversion rates.")
            return None
    else:
        logging.info("Failed to retrieve data from API.")
        return None


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я эхобот на aiogram 3. Отправь мне любое сообщение, и я повторю его.", reply_markup=kb1)


@dp.message(Command("ура"))
async def send_ura(message: types.Message):
    await message.answer("УРАААА! Я эхобот на aiogram 3. Отправь мне любое сообщение, и я повторю его.", reply_markup=kb2)


@dp.message(Command("fox"))
async def send_fox(message: types.Message):
    image_fox = await fox()
    if image_fox:
        await bot.send_photo(message.chat.id, image_fox)
    else:
        await message.answer("Не удалось получить изображение лисы")


@dp.message(Command("лиса"))
async def send_fox_ru(message: types.Message):
    image_fox = await fox()
    if image_fox:
        await bot.send_photo(message.chat.id, image_fox)
    else:
        await message.answer("Не удалось получить изображение лисы")


@dp.message(F.text.func(lambda text: "ура" in text.lower()))
async def respond_ura(message: types.Message):
    await message.answer("УРАААА!")


@dp.message(F.text.func(lambda text: "инфо" in text.lower()))
async def send_info(message: types.Message):
    user_name = message.chat.id
    await message.answer(str(user_name))


@dp.message(Command("weather"))
async def send_weather(message: types.Message):
    city = message.text.split("/weather ")[-1]
    if not city:
        await message.answer("Введите название города после команды, например, /weather London")
        return
    weather_info = get_weather(city)
    if weather_info:
        await message.answer(
            f"Погода в {city}:\n"
            f"Температура: {weather_info['temperature']}°C\n"
            f"Описание: {weather_info['description']}\n"
            f"Влажность: {weather_info['humidity']}%\n"
            f"Давление: {weather_info['pressure']} hPa\n"
            f"Скорость ветра: {weather_info['wind_speed']} м/с"
        )
    else:
        await message.answer("Не удалось получить данные о погоде. Проверьте название города.")


@dp.message(Command("exchange"))
async def send_exchange_rate(message: types.Message):
    args = message.text.split()[1:]
    if len(args) != 2:
        await message.answer("Использование: /exchange FROM_CURRENCY TO_CURRENCY, например, /exchange USD EUR")
        return
    from_currency, to_currency = args
    logging.info(f"Requesting exchange rate from {from_currency} to {to_currency}")
    rate = get_exchange_rate(from_currency, to_currency)
    logging.info(f"Retrieved rate: {rate}")
    if rate:
        await message.answer(f"Курс {from_currency.upper()} к {to_currency.upper()}: {rate}")
    else:
        await message.answer("Не удалось получить курс валют. Проверьте введённые валюты.")


@dp.message()
async def echo(message: types.Message):
    await message.answer(message.text)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())