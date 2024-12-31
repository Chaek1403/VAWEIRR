import json

import aiohttp
from .. import loader, utils
from telethon import events

available_models = {
    "1": "gpt-4o",
    "2": "Command-R+",
    "3": "gpt-4o-mini",
    "4": "gemini",
    "5": "llama-3.1",
    "6": "copilot",
    "7": "qwen",
    "8": "claude-3-haiku",
    "9": "claude-3.5-sonnet"
}

# Путь к файлу для хранения личностей
PERSONAS_FILE = "personas.json"


# Функция для загрузки личностей из файла
def load_personas():
    try:
        with open(PERSONAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# Функция для сохранения личностей в файл
def save_personas(personas):
    with open(PERSONAS_FILE, "w", encoding="utf-8") as f:
        json.dump(personas, f, indent=4)


# Загружаем личности при запуске модуля
personas = load_personas()


@loader.tds
class AIModule(loader.Module):
    """
    🧠 Модуль для общения с ИИ. 
    >>модуль является частью экосистемы Zetta - AI models<<

    Режимы работы:
     - **Одиночный запрос:** `.ai <запрос>` - быстрый ответ на вопрос без сохранения истории.
     - **Чат:** `.chat` - диалог с ИИ, запоминающим контекст беседы.
    """
    strings = {"name": "Zetta - AI models"}

    def __init__(self):
        super().__init__()
        self.default_model = "gpt-4o-mini"
        self.active_chats = {}
        self.chat_history = {}
        self.chat_archive = {}
        self.role = {}
        self.response_mode = {}

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.active_chats = self.db.get("AIModule", "active_chats", {})
        self.chat_history = self.db.get("AIModule", "chat_history", {})
        self.chat_archive = self.db.get("AIModule", "chat_archive", {})
        self.role = self.db.get("AIModule", "role", {})
        self.response_mode = self.db.get("AIModule", "response_mode", {})

    @loader.unrestricted
    async def modelcmd(self, message):
        """
        Устанавливает модель по умолчанию.
        Использование: `.model <номер>` или `.model list` для списка.
        """
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("🤔 <b>Укажите номер модели или list для просмотра списка.</b>")
            return

        if args == "list":
            model_list = "\n".join([f"<b>{k}.</b> {v}" for k, v in available_models.items()])
            await message.edit(f"📝 <b>Доступные модели:</b>\n{model_list}")
            return

        if args not in available_models:
            await message.edit("🚫 <b>Неверный номер модели.</b>")
            return

        self.default_model = available_models[args]
        await message.edit(f"✅ <b>Модель изменена на:</b> {self.default_model}")

    @loader.unrestricted
    async def chatcmd(self, message):
        """
        Включает/выключает режим чата.
        Использование: `.chat`
        """
        chat_id = str(message.chat_id)
        if self.active_chats.get(chat_id):
            self.active_chats.pop(chat_id, None)
            self.db.set("AIModule", "active_chats", self.active_chats)

            if chat_id in self.chat_history:
                self.chat_archive[chat_id] = self.chat_history[chat_id]
                self.chat_history.pop(chat_id, None)
                self.db.set("AIModule", "chat_history", self.chat_history)
                self.db.set("AIModule", "chat_archive", self.chat_archive)
                await message.edit("📴 <b>Режим чата выключен. История архивирована.</b>")
            else:
                await message.edit("📴 <b>Режим чата выключен.</b>")
        else:
            self.active_chats[chat_id] = True
            self.db.set("AIModule", "active_chats", self.active_chats)

            if chat_id in self.chat_archive:
                self.chat_history[chat_id] = self.chat_archive[chat_id]
                self.chat_archive.pop(chat_id, None)
                self.db.set("AIModule", "chat_history", self.chat_history)
                self.db.set("AIModule", "chat_archive", self.chat_archive)
                await message.edit("💬 <b>Режим чата включен. История загружена.</b>")
            else:
                await message.edit("💬 <b>Режим чата включен.</b>")

    @loader.unrestricted
    async def clearcmd(self, message):
        """
        Сбрасывает историю диалога.
        Использование: `.clear`
        """
        chat_id = str(message.chat_id)
        if chat_id in self.chat_history or chat_id in self.chat_archive:
            self.chat_history.pop(chat_id, None)
            self.chat_archive.pop(chat_id, None)
            self.db.set("AIModule", "chat_history", self.chat_history)
            self.db.set("AIModule", "chat_archive", self.chat_archive)
            await message.edit("🗑️ <b>История диалога очищена.</b>")
        else:
            await message.edit("📭️ <b>История диалога пуста.</b>")

    @loader.unrestricted
    async def rolecmd(self, message):
        """
        Устанавливает роль для ИИ в режиме чата.
        Использование: `.role <роль>`
        """
        chat_id = str(message.chat_id)
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("🎭 <b>Укажите роль для ИИ.</b>")
            return

        self.role[chat_id] = args
        self.db.set("AIModule", "role", self.role)
        await message.edit(f"🎭 <b>Роль ИИ установлена:</b> {args}")

    @loader.unrestricted
    async def modecmd(self, message):
        """
        Устанавливает режим ответа ИИ.
        Использование: `.mode <reply/all>`
        """
        chat_id = str(message.chat_id)
        args = utils.get_args_raw(message)
        if not args or args not in ("reply", "all"):
            await message.edit("🤔 <b>Укажите режим ответа: reply или all.</b>")
            return

        self.response_mode[chat_id] = args
        self.db.set("AIModule", "response_mode", self.response_mode)
        await message.edit(f"✅ <b>Режим ответа установлен на:</b> {args}")

    @loader.unrestricted
    async def createpersonacmd(self, message):
        """
        Создает новую личность.
        Использование: `.createpersona <имя> <роль>`
        """
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("🤔 <b>Укажите имя и роль для личности.</b>")
            return

        try:
            name, role = args.split(" ", 1)
        except ValueError:
            await message.edit("🤔 <b>Неверный формат. Используйте: .createpersona <имя> <роль></b>")
            return

        # Изменено: chat_id заменен на 'global'
        if 'global' not in personas:
            personas['global'] = {}
        personas['global'][name] = role
        save_personas(personas)  # Сохраняем изменения в файл
        await message.edit(f"✅ <b>Личность {name} создана.</b>")

    @loader.unrestricted
    async def personascmd(self, message):
        """
        Показывает список личностей.
        Использование: `.personas`
        """
        # Изменено: chat_id заменен на 'global'
        if 'global' not in personas or not personas['global']:
            await message.edit("🤔 <b>Список личностей пуст.</b>")
            return

        persona_list = "\n".join([f"<b>{name}:</b> {role}" for name, role in personas['global'].items()])
        await message.edit(f"📝 <b>Доступные личности:</b>\n{persona_list}")

    @loader.unrestricted
    async def switchpersonacmd(self, message):
        """
        Переключается на указанную личность.
        Использование: `.switchpersona <имя>`
        """
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("🤔 <b>Укажите имя личности.</b>")
            return

        # Изменено: chat_id заменен на 'global'
        if 'global' not in personas or args not in personas['global']:
            await message.edit("🚫 <b>Личность не найдена.</b>")
            return

        chat_id = str(message.chat_id)
        self.role[chat_id] = personas['global'][args]
        await message.edit(f"✅ <b>Переключено на личность:</b> {args}")

    @loader.unrestricted
    async def deletepersonacmd(self, message):
        """
        Удаляет личность.
        Использование: `.deletepersona <имя>`
        """
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("🤔 <b>Укажите имя личности.</b>")
            return

        # Изменено: chat_id заменен на 'global'
        if 'global' not in personas or args not in personas['global']:
            await message.edit("🚫 <b>Личность не найдена.</b>")
            return

        del personas['global'][args]
        save_personas(personas)  # Сохраняем изменения в файл
        await message.edit(f"✅ <b>Личность {args} удалена.</b>")

    @loader.unrestricted
    async def aicmd(self, message):
        """
        Отправляет одиночный запрос к ИИ.
        Использование: `.ai <запрос>` или ответить на сообщение с `.ai`
        """
        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)

        if reply:
            request_text = reply.raw_text
        elif args:
            request_text = args
        else:
            await message.edit("🤔 <b>Введите запрос или ответьте на сообщение.</b>")
            return

        await self.process_request(message, request_text)

    async def process_request(self, message, request_text):
        """
        Обрабатывает запрос к API модели ИИ.
        """
        api_url = "http://api.onlysq.ru/ai/v2"
        chat_id = str(message.chat_id)

        payload = {
            "model": self.default_model,
            "request": {
                "messages": [
                    {
                        "role": "user",
                        "content": request_text
                    }
                ]
            }
        }

        try:
            await message.edit("🤔 <b>Думаю...</b>")

            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    answer = data.get("answer", "🚫 <b>Ответ не получен.</b>").strip()

                    formatted_answer = f"❔ <b>Запрос:</b>\n`{request_text}`\n\n💡 <b>Ответ модели {self.default_model}:</b>\n{answer}"
                    await message.edit(formatted_answer)

        except aiohttp.ClientError as e:
            await message.edit(f"⚠️ <b>Ошибка при запросе к API:</b> {e}\n\n💡 <b>Попробуйте поменять модель или проверить код модуля.</b>")

    @loader.unrestricted
    async def watcher(self, message):
        """
        Следит за сообщениями и отвечает, если активен режим чата.
        """
        chat_id = str(message.chat_id)
        if self.active_chats.get(chat_id):
            # Проверка режима ответа
            if self.response_mode.get(chat_id, "all") == "reply" and not message.is_reply:
                return  # Игнорируем сообщение, если режим "reply" и это не ответ

            # Проверяем, что сообщение текстовое
            if message.text:
                question = message.text.strip()
                user_name = await self.get_user_name(message)  # Получаем имя пользователя
                # Добавляем имя к запросу, сохраняя в историю
                await self.respond_to_message(message, user_name, question)

    async def get_user_name(self, message):
        """
        Возвращает имя пользователя из сообщения.
        """
        if message.sender:
            user = await self.client.get_entity(message.sender_id)
            return user.first_name or user.username
        else:
            return "Аноним"  # Или другой вариант по умолчанию

    async def respond_to_message(self, message, user_name, question):  # Изменено: добавлен аргумент user_name
        """
        Обрабатывает вопрос и отправляет ответ с учетом истории.
        """
        chat_id = str(message.chat_id)

        if chat_id not in self.chat_history:
            self.chat_history[chat_id] = []

        # Сохраняем имя пользователя и сообщение в историю
        self.chat_history[chat_id].append({
            "role": "user",
            "content": f"{user_name} написал: {question}"
        })

        if len(self.chat_history[chat_id]) > 1000:
            self.chat_history[chat_id] = self.chat_history[chat_id][-1000:]

        api_url = "http://api.onlysq.ru/ai/v2"

        payload = {
            "model": self.default_model,
            "request": {
                "messages": [
                    {"role": "system", "content": self.role.get(chat_id, "")}
                ] + self.chat_history[chat_id]
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    answer = data.get("answer", "🚫 <b>Ответ не получен.</b>").strip()

                    self.chat_history[chat_id].append({
                        "role": "assistant",
                        "content": answer
                    })
                    self.db.set("AIModule", "chat_history", self.chat_history)

                    await message.respond(f"<b>Ответ модели {self.default_model}:</b>\n{answer}")

        except aiohttp.ClientError as e:
            await message.respond(f"⚠️ <b>Ошибка при запросе к API:</b> {e}\n\n💡 <b>Попробуйте поменять модель или проверить код модуля.</b>")

    @loader.unrestricted
    async def moduleinfocmd(self, message):  # Changed command name
        """
        Дополнительная информация о модуле и других проектах.
        """
        info_text = """
         <b>Дополнительная информация:</b>

<b>Автор:</b> VAWEIRR

<b>модуль является частью экосистемы Zetta - AI models.</b>
И весь его потенциал вы можете раскрыть используя моего бота: @gpt4o_freetouse_bot

        """
        await message.edit(info_text)
