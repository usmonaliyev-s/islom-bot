import logging
from aiogram import Bot, Dispatcher, Router, types
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from aiogram.filters import Command
from aiogram.enums import ParseMode
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from hijri_converter import convert

TOKEN = "7979914433:AAF3-wqElpMmntufWhtHc2YJUKQKxqBh568"

# Logging
logging.basicConfig(level=logging.INFO)

# Initialize bot & dispatcher
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()


# Main keyboard
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="Namoz vaqtlari")]
    ],
    resize_keyboard=True
)

# Regions keyboard
regions_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Andijon", callback_data="Andijon"),
        InlineKeyboardButton(text="Buxoro", callback_data="Buxoro"),
    ],
    [
        InlineKeyboardButton(text="Farg'ona", callback_data="Farg'ona"),
        InlineKeyboardButton(text="Jizzax", callback_data="Jizzax"),
    ],
    [
        InlineKeyboardButton(text="Xorazm", callback_data="Urganch"),
        InlineKeyboardButton(text="Namangan", callback_data="Namangan"),
    ],
    [
        InlineKeyboardButton(text="Navoiy", callback_data="Navoiy"),
        InlineKeyboardButton(text="Qashqadaryo", callback_data="Qarshi"),
    ],
    [
        InlineKeyboardButton(text="Qoraqalpogʻiston", callback_data="Nukus"),
        InlineKeyboardButton(text="Samarqand", callback_data="Samarqand"),
    ],
    [
        InlineKeyboardButton(text="Sirdaryo", callback_data="Guliston"),
        InlineKeyboardButton(text="Surxondaryo", callback_data="Termiz"),
    ],
    [
        InlineKeyboardButton(text="Toshkent", callback_data="Toshkent")
    ]
])

def extract_text(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text().strip()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        f"<b>Assalomu alaykum {message.from_user.first_name}!</b>\n\nViloyatlardan birini tanlang",
        reply_markup=regions_keyboard
    )

@dp.callback_query()
async def send_times(callback: types.CallbackQuery):
    data = callback.data

    if data == "back":
        await callback.message.delete()
        await start_cmd(callback.message)
    else:
        response = requests.get(f"https://islomapi.uz/api/present/day?region={data}")
        json_data = response.json()

        region = json_data["region"]
        date = json_data["date"]
        weekday = json_data["weekday"]
        times = json_data["times"]

        saharlik = times["tong_saharlik"]
        quyosh = times["quyosh"]
        peshin = times["peshin"]
        asr = times["asr"]
        shom = times["shom_iftor"]
        hufton = times["hufton"]

        war = datetime.strptime(date, '%Y-%m-%d')
        war1 = convert.Gregorian.fromdate(war).to_hijri()

        hijri_year = war1.year
        hijri_date = war1.day
        hijri_month = war1.month_name()

        message_text = f"""<b>
Namoz vaqtlari 2️⃣0️⃣2️⃣5️⃣

🌆 {region}

{date} | {hijri_year}-yil {hijri_date}-{hijri_month} | {weekday}

Bomdod: {saharlik}
Quyosh: {quyosh}
Peshin: {peshin}
Asr: {asr}
Shom: {shom}
Xufton: {hufton}

<i>@namoz_vaqti_uzbekistan</i></b>
"""


        share_buttons = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✉️ Ulashish",
                    switch_inline_query=extract_text(message_text).replace("Namoz vaqtlari", "\n\nNamoz vaqtlari")
                )
            ],
            [
                InlineKeyboardButton(text="🔙 Ortga", callback_data="back")
            ]
        ])

        await callback.message.edit_text(
            text=message_text,
            reply_markup=share_buttons
        )

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
