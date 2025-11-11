import asyncio
import logging
import os
from html import escape
from typing import Iterable, Sequence

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.exceptions import TelegramAPIError

import storage


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable '{name}' must be set")
    return value


TOKEN = _get_required_env("BOT_TOKEN")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

logger = logging.getLogger(__name__)


async def _notify_users(users: Iterable[int], text: str) -> None:
    for user_id in users:
        try:
            await bot.send_message(user_id, text)
        except TelegramAPIError as exc:
            logger.warning("Failed to notify user %s: %s", user_id, exc)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    created = storage.add_user(user_id)
    if created:
        await message.answer("ثبت نام انجام شد. اطلاعیه‌ها اینجا ارسال می‌شود.")
    else:
        await message.answer("پیش‌تر ثبت‌نام کرده‌اید و اطلاعیه‌ها به اینجا ارسال می‌شود.")


@dp.message(Command(commands=["register"]))
async def cmd_register(message: Message):
    await cmd_start(message)


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
    lowered = text.casefold()
    return [kw for kw in storage.get_keywords() if kw.casefold() in lowered]


def _get_message_content(message: Message) -> str | None:
    return message.text or message.caption


def _format_notification(message: Message, keywords: Sequence[str], content: str) -> str:
    chat_label = message.chat.title or message.chat.full_name or str(message.chat.id)
    escaped_keywords = ", ".join(escape(kw) for kw in keywords)
    escaped_chat = escape(chat_label)
    sender = message.from_user.full_name if message.from_user else "کاربر ناشناس"
    escaped_sender = escape(sender)
    escaped_content = escape(content)
    return (
        f"کلیدواژه‌های [{escaped_keywords}] در گفتگو «{escaped_chat}» یافت شد:\n"
        f"{escaped_sender}: {escaped_content}"
    )


async def _handle_matches(notify_text: str) -> None:
    await _notify_users(storage.get_users(), notify_text)


@dp.message()
async def monitor(message: Message):
    content = _get_message_content(message)
    if not content:
        return

    chat_id = message.chat.id
    if chat_id not in storage.get_groups():
        return

    found = _extract_keywords(content)
    if not found:
        return

    notify_text = _format_notification(message, found, content)
    await _handle_matches(notify_text)


async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
