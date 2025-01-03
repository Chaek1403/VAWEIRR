import json
import os  # Импортируем os

import aiohttp
import requests
from telethon import events
from .. import loader, utils
import re

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
        self.module_instructions = self.get_module_instruction()

    @loader.unrestricted
    async def aisupcmd(self, message):
        """
        Спросить у AI помощника.
        Использование: `.aisup <запрос>` или ответить на сообщение с `.aisup`
        """
        r = "sup"
        await self.process_request(message, self.instructions, r)

    @loader.unrestricted
    async def aierrorcmd(self, message):
        """
        Спросить у AI помощника об ошибке модуля.
        Использование: `.aierror <запрос>` или ответить на сообщение с `.aierror`
        """
        r = "error"
        await self.process_request(message, self.error_instructions, r)

    def get_instructions(self):
        url = 'https://raw.githubusercontent.com/Chaek1403/VAWEIRR/refs/heads/main/instruction.txt'
        response = requests.get(url)
        return response.text

    def get_error_instructions(self):
        url = 'https://raw.githubusercontent.com/Chaek1403/VAWEIRR/refs/heads/main/error_instruction.txt'
        response = requests.get(url)
        return response.text

    def get_module_instruction(self):
        url = 'https://raw.githubusercontent.com/Chaek1403/VAWEIRR/refs/heads/main/module_instruction.txt'
        response = requests.get(url)
        return response.text

    @loader.unrestricted
    async def aicreatecmd(self, message):
        """
        Попросить AI помощника написать модуль.
        Использование: `.aicreate <запрос>` или ответить на сообщение с `.aicreate`
        """
        r = "create"
        await self.process_request(message, self.module_instructions, r)

    async def save_and_send_code(self, answer, message):
        """Сохраняет код в файл, отправляет его и удаляет."""
        try:
            # Создаем файл AI-module.py и записываем в него код
            code_start = answer.find("`python") + len("`python")
            code_end = answer.find("```", code_start)
            code = answer[code_start:code_end].strip()
    
            with open("AI-module.py", "w") as f:
                f.write(code)
    
            # Отправляем файл в чат
            await message.client.send_file(
                message.chat_id,
                "AI-module.py",
                caption="<b>💫Ваш готовый модуль</b>",
            )
    
            # Удаляем файл
            os.remove("AI-module.py")
    
        except (TypeError, IndexError) as e:  # Обработка конкретных исключений
            await message.reply(f"Ошибка при извлечении кода: {e}")
        except Exception as e:  # Обработка любых других исключений
            await message.reply(f"Ошибка при обработке кода: {e}")


    async def process_request(self, message, instructions, command):
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
                        "role": "user",
                        "content": f"{instructions}\nЗапрос пользователя: {request_text}"
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

                    if command == "error":
                        formatted_answer = f"💡<b> Ответ AI-помощника по Hikka | Спец. по ошибкам</b>:\n{answer}"
                        await message.edit(formatted_answer)
                    elif command == "sup":
                        formatted_answer = f"❔ Запрос:\n`{request_text}`\n\n💡 <b>Ответ AI-помощника по Hikka</b>:\n{answer}"
                        await message.edit(formatted_answer)
                    elif command == "create":
                        await message.delete()
                        await message.respond(f"<b>Ответ AI-помощника по Hikka | Креатор модулей</b>:\n{answer}")
                        # Вызываем функцию для сохранения и отправки кода
                        await self.save_and_send_code(answer, message)
                    else:
                        formatted_answer = answer
                        await message.edit(formatted_answer)

        except aiohttp.ClientError as e:
            await message.edit(f"⚠️ Ошибка при запросе к API: {e}\n\n💡 Попробуйте поменять модель или проверить код модуля.")
            
