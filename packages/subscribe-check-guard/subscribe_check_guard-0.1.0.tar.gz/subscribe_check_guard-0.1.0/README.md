# subscribe_check_guard

`subscribe_check_guard` — это лёгкая библиотека для **aiogram**, которая упрощает работу с проверкой подписки на Telegram-каналы и управлением администраторами бота.

---

## 📌 Badges

[![PyPI version](https://img.shields.io/pypi/v/subscribe_check_guard)](https://pypi.org/project/subscribe_check_guard/)  
[![Python Version](https://img.shields.io/pypi/pyversions/subscribe_check_guard)](https://www.python.org/)  
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)  
[![GitHub last commit](https://img.shields.io/github/last-commit/k1ng-ali/subscribe_check_guard)](https://github.com/k1ng-ali/subscribe_check_guard)

---

## 📦 Installation

```bash
pip install subscribe_check_guard
```

---
## Usage
```python
from aiogram.types import Message
from aiogram.filters import Command
from subscribe_check_guard import set_channel, check_subscribe

# Добавление нового канала (только для админов)
@dp.message(Command("set_channel"))
@set_channel()
async def add_channel(msg: Message):
    pass

# Проверка подписки пользователя на обязательные каналы
@dp.message()
@check_subscribe()
async def handle_message(msg: Message):
    await msg.answer("Вы подписаны на все каналы ✅")

```
---

## 🔐 Adding an admin
После установки библиотеки необходимо добавить хотя бы одного администратора:
```python
from subscribe_check_guard import setup_superuser

async def main():
    setup_superuser("123456789")  # замените на ваш Telegram ID
```

---
## 
🛠 Managing admins and channels
```python
from aiogram.types import Message
from aiogram.filters import Command
from subscribe_check_guard import set_admin, del_admin, set_channel, del_channel

# Добавление администратора
@dp.message(Command("set_admin"))
@set_admin()
async def add_admin(msg: Message):
    pass

# Удаление администратора
@dp.message(Command("del_admin"))
@del_admin()
async def remove_admin(msg: Message):
    pass

# Добавление канала в список обязательных
@dp.message(Command("set_channel"))
@set_channel()
async def add_channel(msg: Message):
    pass

# Удаление канала из списка обязательных
@dp.message(Command("del_channel"))
@del_channel()
async def remove_channel(msg: Message):
    pass
```
❕Команды для бота могут быть любыми (это то, что внутри Command()).

---
## 🧠 Optional initialization
Если вы хотите вручную загрузить данные из файлов при старте бота:
```python
from subscribe_check_guard import init_storage

# Загружает список админов и каналов в память
init_storage()
```
⚠️ Для первой версии библиотеки init_storage() вызывается автоматически при импорте, так что этот шаг можно пропустить.

---
## 💬 Community / Contributing

Этот проект открыт для сообщества! Если у вас есть идеи по улучшению библиотеки, баги или предложения новых функций, вы можете:

- Открыть issue
 на GitHub

- Создать pull request с вашими изменениями

- Поделиться своим опытом использования библиотеки

Любая помощь и обратная связь приветствуются! 🙌

---
## 📄 License
MIT License © 2025 MuhammadAli Astanaqulov
