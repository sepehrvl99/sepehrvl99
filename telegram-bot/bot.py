import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from configparser import ConfigParser
import notifier
import storage

config = ConfigParser()
config.read('config.ini')
TOKEN = config['Telegram']['Token']

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(CommandStart())
async def cmd_start(message: Message):
    data = storage.load_data()
    user_id = message.from_user.id
    data['user_id'] = user_id
    storage.save_data(data)
    await message.answer("ثبت نام انجام شد. اطلاعیه‌ها اینجا ارسال می‌شود.")

@dp.message(Command(commands=["addgroup"]))
async def add_group(message: Message):
    data = storage.load_data()
    args = message.text.split(maxsplit=1)
    if len(args) == 2 and args[1].isdigit():
        group_id = int(args[1])
        if group_id not in data['groups']:
            data['groups'].append(group_id)
            storage.save_data(data)
            await message.answer(f"گروه {group_id} اضافه شد.")
        else:
            await message.answer("این گروه قبلاً اضافه شده است.")
    else:
        await message.answer("نحوه استفاده: /addgroup <group_chat_id>")

@dp.message(Command(commands=["addkeyword"]))
async def add_keyword(message: Message):
    data = storage.load_data()
    args = message.text.split(maxsplit=1)
    if len(args) == 2:
        keyword = args[1].strip()
        if keyword and keyword not in data['keywords']:
            data['keywords'].append(keyword)
            storage.save_data(data)
            await message.answer(f"کلیدواژه '{keyword}' اضافه شد.")
        else:
            await message.answer("این کلیدواژه قبلاً اضافه شده یا خالی است.")
    else:
        await message.answer("نحوه استفاده: /addkeyword <keyword>")

@dp.message(Command(commands=["list"]))
async def list_items(message: Message):
    data = storage.load_data()
    reply = f"گروه‌های مانیتور: {data['groups']}\nکلیدواژه‌ها: {data['keywords']}"
    await message.answer(reply)

@dp.message()
async def monitor(message: Message):
    data = storage.load_data()
    chat_id = message.chat.id
    if chat_id in data['groups'] and message.text:
        text = message.text.lower()
        found = [kw for kw in data['keywords'] if kw.lower() in text]
        if found:
            notify_text = (
                f"کلیدواژه‌های {found} در گروه {chat_id} یافت شد:\n"
                f"{message.from_user.full_name}: {message.text}"
            )
            await bot.send_message(data['user_id'], notify_text)
            notifier.send_email("هشدار کلیدواژه", notify_text)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())