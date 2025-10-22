import os
import json
from functools import wraps
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Конфигурация ---
ADMINS_FILE = "admins.json"
CHANNELS_FILE = "channels.json"

# --- Хранилище в памяти ---
ADMINS: list[str] = []
CHANNELS: list[str] = []


# --- Работа с файлами ---
def load_json(filename: str) -> list[str]:
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_json(filename: str, data: list[str]):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- Инициализация при запуске ---
def init_storage():
    global ADMINS, CHANNELS
    ADMINS = load_json(ADMINS_FILE)
    CHANNELS = load_json(CHANNELS_FILE)

# --- Работа с Админ ID ---
def setup_superuser(admin_id: str):
    if admin_id not in ADMINS:
        ADMINS.append(admin_id)
        save_json(ADMINS_FILE, ADMINS)

def set_admin():
    def decorator(func):
        @wraps(func)
        @admin_only
        async def wrapper(msg: Message, *args, **kwargs):
            parts = msg.text.split()
            if len(parts) < 2:
                await msg.answer("⚠️ Укажите ID нового администратора, например:\n`/set_admin 123456789`", parse_mode="Markdown")
                return

            new_admin = parts[1]
            if new_admin not in ADMINS:
                ADMINS.append(new_admin)
                await msg.answer(f"✅ Пользователь {new_admin} добавлен в список администраторов бота")
                save_json(ADMINS_FILE, ADMINS)
            else:
                await msg.answer(f"ℹ️ Пользователь {new_admin} уже есть в списке администраторов бота")
            return await func(msg, *args, **kwargs)
        return wrapper
    return decorator

def del_admin():
    def decorator(func):
        @wraps(func)
        @admin_only
        async def wrapper(msg: Message, *args, **kwargs):
            parts = msg.text.split()
            if len(parts) < 2:
                await msg.answer("⚠️ Укажите ID нового администраторов, например:\n`/set_admin 123456789`", parse_mode="Markdown")
                return

            new_admin = parts[1]
            if new_admin in ADMINS:
                ADMINS.remove(new_admin)
                await msg.answer(f"✅ Пользователь {new_admin} убран из списка администраторов бота")
                save_json(ADMINS_FILE, ADMINS)
            else:
                await msg.answer(f"ℹ️ Пользователь {new_admin} нет в списке администраторов бота")
            return await func(msg, *args, **kwargs)
        return wrapper
    return decorator

# --- Декоратор для установки канала ---
def set_channel():
    def decorator(func):
        @admin_only
        @wraps(func)
        async def wrapper(msg: Message, *args, **kwargs):
            parts = msg.text.split()
            if len(parts) < 2:
                await msg.answer("⚠️ Укажите канал, например:\n`/set_channel @example`", parse_mode="Markdown")
                return

            channel = parts[1]
            if channel not in CHANNELS:
                CHANNELS.append(channel)
                save_json(CHANNELS_FILE, CHANNELS)
                await msg.answer(f"✅ Канал {channel} добавлен в список обязательных.")
            else:
                await msg.answer(f"ℹ️ Канал {channel} уже есть в списке.")
            return await func(msg, *args, **kwargs)
        return wrapper
    return decorator

def del_channel():
    def decorator(func):
        @admin_only
        @wraps(func)
        async def wrapper(msg: Message, *args, **kwargs):
            parts = msg.text.split()
            if len(parts) < 2:
                await msg.answer("⚠️ Укажите канал, например:\n`/set_channel @example`", parse_mode="Markdown")
                return

            channel = parts[1]
            if channel in CHANNELS:
                CHANNELS.remove(channel)
                save_json(CHANNELS_FILE, CHANNELS)
                await msg.answer(f"✅ Канал {channel} убран из список обязательных.")
            else:
                await msg.answer(f"ℹ️ Канал {channel} нет в списке обязательных.")
            return await func(msg, *args, **kwargs)

        return wrapper

    return decorator

# --- Декоратор проверки подписки ---
def check_subscribe():
    def decorator(func):
        @wraps(func)
        async def wrapper(msg: Message, *args, **kwargs):
            bot = msg.bot
            user_id = msg.from_user.id
            blocked_channels = []

            for ch in CHANNELS:
                try:
                    member = await bot.get_chat_member(ch, user_id)
                    if member.status == "left":
                        blocked_channels.append(ch)
                except (TelegramBadRequest, TelegramForbiddenError):
                    # Бот потерял доступ, уведомляем админов
                    for admin_id in ADMINS:
                        await bot.send_message(admin_id, f"⚠️ Бот не имеет доступа к {ch}")
                    continue  # просто пропускаем канал при проверке подписки пользователя

            if blocked_channels:
                await msg.answer(
                    "❗️Чтобы пользоваться ботом, подпишитесь на каналы:",
                    reply_markup=make_channels_keyboard(blocked_channels)
                )
                return

            return await func(msg, *args, **kwargs)
        return wrapper
    return decorator


# --- Utils ---
async def check_channels_access(bot):
    for ch in CHANNELS:
        try:
            await bot.get_chat(ch)  # просто пытаемся получить инфо о канале
        except (TelegramBadRequest, TelegramForbiddenError):
            for admin_id in ADMINS:
                await bot.send_message(admin_id, f"⚠️ Бот потерял доступ к каналу {ch}")


def admin_only(func):
    @wraps(func)
    async def wrapper(msg: Message, *args, **kwargs):
        if str(msg.from_user.id) not in ADMINS:
            await msg.answer("⛔ Команда доступна только администраторам.")
            return
        return await func(msg, *args, **kwargs)
    return wrapper


# --- Клавиатура с кнопками подписки ---
def make_channels_keyboard(channels: list[str]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"Перейти в {ch}", url=f"https://t.me/{ch.replace('@', '')}")]
        for ch in channels
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

init_storage()