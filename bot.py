import asyncio
import os
from typing import Iterable

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

import storage


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable '{name}' must be set")
    return value


TOKEN = _get_required_env("7376006440:AAHCeJK5zvUMsVIbFfi6avZ0diVMzCphaJg")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())


async def _notify_users(users: Iterable[int], text: str) -> None:
    for user_id in users:
        await bot.send_message(user_id, text)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    created = storage.add_user(user_id)
    if created:
        await message.answer("ثبت نام انجام شد. اطلاعیه‌ها اینجا ارسال می‌شود.")
    else:
        await message.answer("پیش‌تر ثبت‌نام کرده‌اید و اطلاعیه‌ها به اینجا ارسال می‌شود.")


@dp.message(Command(commands=["addgroup"]))
async def add_group(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        await message.answer("نحوه استفاده: /addgroup <group_chat_id>")
        return

    try:
        group_id = int(args[1])
    except ValueError:
        await message.answer("شناسه گروه باید یک عدد باشد.")
        return

    if storage.add_group(group_id):
        await message.answer(f"گروه {group_id} اضافه شد.")
    else:
        await message.answer("این گروه قبلاً اضافه شده است.")


@dp.message(Command(commands=["addkeyword"]))
async def add_keyword(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        await message.answer("نحوه استفاده: /addkeyword <keyword>")
        return

    keyword = args[1].strip()
    if not keyword:
        await message.answer("کلیدواژه نمی‌تواند خالی باشد.")
        return

    if storage.add_keyword(keyword):
        await message.answer(f"کلیدواژه '{keyword}' اضافه شد.")
    else:
        await message.answer("این کلیدواژه قبلاً اضافه شده است.")


@dp.message(Command(commands=["list"]))
async def list_items(message: Message):
    data = storage.load_data()
    reply = (
        f"کاربران ثبت‌شده: {data['users']}\n"
        f"گروه‌های مانیتور: {data['groups']}\n"
        f"کلیدواژه‌ها: {data['keywords']}"
    )
    await message.answer(reply)


def _extract_keywords(text: str) -> list[str]:
    lowered = text.lower()
    return [kw for kw in storage.get_keywords() if kw.lower() in lowered]


async def _handle_matches(notify_text: str) -> None:
    await _notify_users(storage.get_users(), notify_text)


@dp.message()
async def monitor(message: Message):
    if not message.text:
        return

    chat_id = message.chat.id
    if chat_id not in storage.get_groups():
        return

    found = _extract_keywords(message.text)
    if not found:
        return

    notify_text = (
        f"کلیدواژه‌های {found} در گروه {chat_id} یافت شد:\n"
        f"{message.from_user.full_name}: {message.text}"
    )
    await _handle_matches(notify_text)


async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
