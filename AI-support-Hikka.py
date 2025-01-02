import json

import aiohttp
from .. import loader, utils
from telethon import events
import requests  # Импортируем requests

@loader.tds
class AIsupport(loader.Module):
    """
    AI - помощник по Hikka.
    """
    strings = {"name": "AI-sup Hikka"}

    def __init__(self):
        super().__init__()
        self.default_model = "gpt-4o-mini"
        self.instructions = self.get_instructions()
        self.error_instructions = self.get_error_instructions()

    @loader.unrestricted
    async def aisupcmd(self, message):
        """
        Спросить у AI помощника.
        Использование: `.aisup <запрос>` или ответить на сообщение с `.aisup`
        """
        r = True
        await self.process_request(message, self.instructions, r)
       

    @loader.unrestricted
    async def aierrorcmd(self, message):
        """
        Спросить у AI помощника об ошибке модуля.
        Использование: `.aierror <запрос>` или ответить на сообщение с `.aierror`
        """
        r = False
        await self.process_request(message, self.error_instructions, r)

    def get_instructions(self):  # Добавляем self
        url = 'https://raw.githubusercontent.com/Chaek1403/VAWEIRR/refs/heads/main/instruction.txt'
        response = requests.get(url)
        return response.text

    def get_error_instructions(self):
        url = 'https://raw.githubusercontent.com/Chaek1403/VAWEIRR/refs/heads/main/error_instruction.txt'
        response = requests.get(url)
        return response.text

    async def process_request(self, message, instructions, r):
        """
        Обрабатывает запрос к API модели ИИ.
        """
        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)
    
        if reply:
            request_text = reply.raw_text
        elif args:
            request_text = args
        else:
            await message.edit("🤔 Введите запрос или ответьте на сообщение.")
            return
    
        api_url = "http://api.onlysq.ru/ai/v2"
        chat_id = str(message.chat_id)
    
        payload = {
            "model": "gpt-4o-mini",
            "request": {
                "messages": [
                    {
                        "role": "system",
                        "content": instructions  # Используем self.instructions
                    },
                    {
                        "role": "user",
                        "content": request_text
                    }
                ]
            }
        }
    
        try:
            await message.edit("<b>🤔 Думаю...</b>")
    
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    answer = data.get("answer", "🚫 Ответ не получен.").strip()
    
                    
                    command = r
                    if command == False:
                        formatted_answer = f"💡<b>Ответ AI-помощника по Hikka | Спец. По ошибкам</b>:\n{answer}"
                    else:
                        formatted_answer = f"❔ Запрос:\n`{request_text}`\n\n💡 <b>Ответ AI-помощника по Hikka</b>:\n{answer}"
    
                    await message.edit(formatted_answer)
    
        except aiohttp.ClientError as e:
            await message.edit(f"⚠️ Ошибка при запросе к API: {e}\n\n💡 Попробуйте поменять модель или проверить код модуля.")
      
