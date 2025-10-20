<p align="center">
    <img src="assets/logo.svg" alt="PyMax" width="400">
</p>

<p align="center">
    <strong>Python wrapper для API мессенджера Max</strong>
</p>

<p align="center">
    <img src="https://img.shields.io/badge/python-3.10+-3776AB.svg" alt="Python 3.11+">
    <img src="https://img.shields.io/badge/License-MIT-2f9872.svg" alt="License: MIT">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff">
    <img src="https://img.shields.io/badge/packaging-uv-D7FF64.svg" alt="Packaging">
</p>

---
> ⚠️ **Дисклеймер**
> 
> *   Это **неофициальная** библиотека для работы с внутренним API Max.
> *   Использование может **нарушать условия предоставления услуг** сервиса.
> *   **Вы используете её исключительно на свой страх и риск.**
> *   **Разработчики и контрибьюторы не несут никакой ответственности** за любые последствия использования этого пакета, включая, но не ограничиваясь: блокировку аккаунтов, утерю данных, юридические риски и любые другие проблемы.
> *   API может быть изменен в любой момент без предупреждения.
---

## Описание

**`pymax`** — асинхронная Python библиотека для работы с API мессенджера Max. Предоставляет интерфейс для отправки сообщений, управления чатами, каналами и диалогами через WebSocket соединение.

### Основные возможности

- Вход по номеру телефона
- Отправка, редактирование и удаление сообщений
- Работа с чатами и каналами
- История сообщений

## Установка

> [!IMPORTANT]
> Для работы библиотеки требуется Python 3.10 или выше

### Установка через pip

```bash
pip install -U maxapi-python
```

### Установка через uv

```bash
uv add -U maxapi-python
```

## Быстрый старт

### Базовый пример использования

```python
import asyncio
from pymax import MaxClient, Message

# Инициализация клиента
phone = "+1234567890"
client = MaxClient(phone=phone, work_dir="cache")

# Обработчик входящих сообщений
@client.on_message()
async def handle_message(message: Message) -> None:
    print(f"{message.sender}: {message.text}")

# Обработчик запуска клиента
@client.on_start
async def handle_start() -> None:
    print("Клиент запущен")
    
    # Получение истории сообщений
    history = await client.fetch_history(chat_id=0)
    if history:
        for message in history:
            user = await client.get_user(message.sender)
            if user:
                print(f"{user.names[0].name}: {message.text}")

async def main() -> None:
    await client.start()
    
    # Работа с чатами
    for chat in client.chats:
        print(f"Чат: {chat.title}")
        
        # Отправка сообщения
        message = await client.send_message(
            "Привет от PyMax!", 
            chat.id, 
            notify=True
        )
        
        # Редактирование сообщения
        await asyncio.sleep(2)
        await client.edit_message(
            chat.id, 
            message.id, 
            "Привет от PyMax! (отредактировано)"
        )
        
        # Удаление сообщения
        await asyncio.sleep(2)
        await client.delete_message(chat.id, [message.id], for_me=False)
    
    # Работа с диалогами
    for dialog in client.dialogs:
        print(f"Диалог: {dialog.last_message.text}")
    
    # Работа с каналами
    for channel in client.channels:
        print(f"Канал: {channel.title}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Документация

[WIP](https://noxzion.github.io/)

## Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для получения информации.

## Новости

[Telegram](https://t.me/pymax_news)

## Авторы

- **[noxzion](https://github.com/noxzion)** — Оригинальный автор проекта
- **[ink](https://github.com/ink-developer)** — Главный разработчик, исследование API и его документация

## Контрибьюторы

Спасибо всем за помощь в разработке!

<a href="https://github.com/ink-developer/PyMax/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=ink-developer/PyMax" />
</a>
