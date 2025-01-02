import json

import aiohttp
from .. import loader, utils
from telethon import events
import requests  # Импортируем requests

@loader.tds
class AIsupport(loader.Module):
    """
    AI - помощник по Hikka.
    ⚠️Не поможет с ошибками во время установки хикки, или с внешними модулями.
    """
    strings = {"name": "AI-sup Hikka"}

    def __init__(self):
        super().__init__()
        self.default_model = "gpt-4o-mini"
        self.instructions = self.get_instructions()  # Вызываем get_instructions() здесь

    @loader.unrestricted
    async def aisupcmd(self, message):
        """
        Спросить у AI помощника.
        Использование: `.aisup <запрос>` или ответить на сообщение с `.aisup`
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

    def get_instructions(self):  # Добавляем self
        url = 'https://raw.githubusercontent.com/Chaek1403/VAWEIRR/refs/heads/main/instruction.txt'
        response = requests.get(url)
        return response.text

    async def process_request(self, message, request_text):
        """
        Обрабатывает запрос к API модели ИИ.
        """
        api_url = "http://api.onlysq.ru/ai/v2"
        chat_id = str(message.chat_id)

        payload = {
            "model": "gpt-4o-mini",
            "request": {
                "messages": [
                    {
                        "role": "system",
                        "content": self.instructions  # Используем self.instructions
                    },
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
