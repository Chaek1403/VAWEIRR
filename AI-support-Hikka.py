import json
import os  # Импортируем os

import aiohttp
import requests
from telethon import events
from .. import loader, utils
import re
from time import sleep

@loader.tds
class AIsupport(loader.Module):
    """
    AI - помощник по Hikka.
    🌘Version: 3.0 Models of thinking - FULL
    ⚡Разработчик: @procot1
    💚Оригинальный модуль
    """
    strings = {"name": "AI-sup Hikka"}

    def __init__(self):
        super().__init__()
        self.default_model = "gpt-4o-mini"
        self.instructions = self.get_instructions()
        self.error_instructions = self.get_error_instructions()
        self.module_instructions = self.get_module_instruction()
        self.double_instructions = self.get_double_instruction()
        self.allmodule_instruction = self.get_allmodule_instruction()

    @loader.unrestricted
    async def aisupcmd(self, message):
        """
        Спросить у AI помощника.
        Использование: `.aisup <запрос>` или ответить на сообщение с `.aisup`
        
        🧠Скормлены знания: 
        • Установки | команды встроенных модулей | Внешние модули(40 модулей) | чаты Хикки | нюнсы Хикки | официальные тгк с модулями | меры безопасности | Список советов по устранению ошибок | Данные о хикке
        """
        r = "sup"
        await self.process_request(message, self.instructions, r)

    @loader.unrestricted
    async def aierrorcmd(self, message):
        """
        Спросить у AI помощника об ошибке модуля.
        Использование: `.aierror <запрос>` или ответить на сообщение с `.aierror`
        
        🧠Скормлены знания(old data set):
        • команды встроенных модулей | чаты Хикки | больше нюансов и принципов работы Хикки | примеры ошибок и их решений | большой список советов по устранению ошибок
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

    def get_double_instruction(self):
        url = 'https://raw.githubusercontent.com/Chaek1403/VAWEIRR/refs/heads/main/double_instruction.txt'
        response = requests.get(url)
        return response.text
    def get_allmodule_instruction(self):
        url = 'https://raw.githubusercontent.com/Chaek1403/VAWEIRR/refs/heads/main/allmodules.txt'
        response = requests.get(url)
        return response.text

    @loader.unrestricted
    async def aiinfocmd(self, message):
        """
        - Информация об обновлении✅
        """
        await message.edit('''<b>🧬Обновление 3.0:
Изменено:
- Система 'Размышлений' доработана. Теперь перед ответом модель проверяет саму себя 3 раза используя разные дата сеты(знания)

Как это: 
- Модель с дата-сетом(1) дает ответ на запрос.
- затем модель с дата сетом(2) проверяет этот ответ и сверяет его со своими данными.
- затем модель с дата сетом(3) проверяет предыдущий ответ и корректирует его.
- после она дает финальный ответ, который будет более точен и верен.

💫получается такая схема: Запрос>дт1>дт2>дт3>Ответ
🔗Тг канал модуля: https://t.me/hikkagpt</b>''')

    async def allmodule(self, answer, message, request_text):
        chat_id = str(message.chat_id)
        rewrite2 = self.get_allmodule_instruction()
        api_url = "http://api.onlysq.ru/ai/v2"
        sleep(4)

        payload = {
            "model": "gpt-4o-mini",
            "request": {
                "messages": [
                    {
                        "role": "user",
                        "content": f"{rewrite2}\nЗапрос пользователя: {request_text}\nОтвет второй части модуля:{answer}"
                    }
                ]
            }
        }

        try:
            await message.edit("<b>🎭Цепочка размышлений модели в процессе:\n🟢Первая модель приняла решение\n🟢Вторая модель приняла решение.\n💭Третья модель думает...</b>\n\nПочему так долго: каждая модель имеет свой дата сет. И сверяет ответ предыдущей модели с своими знаниями.")

            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    answer = data.get("answer", "🚫 Ответ не получен.").strip()
                    formatted_answer = f"❔ Запрос:\n`{request_text}`\n\n💡 <b>Ответ AI-помощника по Hikka</b>:\n{answer}"
                    await message.edit(formatted_answer)

        except aiohttp.ClientError as e:
            await message.edit(f"⚠️ Ошибка при запросе к API: {e}\n\n💡 Попробуйте поменять модель или проверить код модуля.")

    

    async def rewrite_process(self, answer, message, request_text):
        r = 'rewrite'
        api_url = "http://api.onlysq.ru/ai/v2"
        chat_id = str(message.chat_id)
        rewrite = self.get_double_instruction()

        payload = {
            "model": "gpt-4o-mini",
            "request": {
                "messages": [
                    {
                        "role": "user",
                        "content": f"{rewrite}\nЗапрос пользователя: {request_text}\nОтвет первой части модуля:{answer}"
                    }
                ]
            }
        }

        try:
            await message.edit("<b>🎭Цепочка размышлений модели в процессе:\n🟢Первая модель приняла решение\n💭Вторая модель думает...</b>\n\nПочему так долго: каждая модель имеет свой дата сет. И сверяет ответ предыдущей модели с своими знаниями.")

            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    answer = data.get("answer", "🚫 Ответ не получен.").strip()
                    await self.allmodule(answer, message, request_text)

        except aiohttp.ClientError as e:
            await message.edit(f"⚠️ Ошибка при запросе к API: {e}\n\n💡 Попробуйте поменять модель или проверить код модуля.")



    @loader.unrestricted
    async def aicreatecmd(self, message):
        """
        Попросить AI помощника написать модуль.
        Использование: `.aicreate <запрос>` или ответить на сообщение с `.aicreate`
        
        🧠Скормлены знания:
        • Вся документация по написанию модулей Hikka (кроме Hikka only) | мелкие наводящие инструкции
        """
        r = "create"
        await self.process_request(message, self.module_instructions, r)

    async def save_and_send_code(self, answer, message):
        """Сохраняет код в файл, отправляет его и удаляет."""
        try:
            code_start = answer.find("`python") + len("`python")
            code_end = answer.find("```", code_start)
            code = answer[code_start:code_end].strip()
    
            with open("AI-module.py", "w") as f:
                f.write(code)
    
            await message.client.send_file(
                message.chat_id,
                "AI-module.py",
                caption="<b>💫Ваш готовый модуль</b>",
            )
    
            os.remove("AI-module.py")
    
        except (TypeError, IndexError) as e:
            await message.reply(f"Ошибка при извлечении кода: {e}")
        except Exception as e:  
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
                        await message.edit("<b>💬Размышления моделей начались..</b>")
                        await self.rewrite_process(answer, message, request_text)
                    elif command == "create":
                        await message.delete()
                        await message.respond(f"<b>Ответ AI-помощника по Hikka | Креатор модулей</b>:\n{answer}")
                        await self.save_and_send_code(answer, message)
                    elif command == 'rewrite':
                        formatted_answer = f"❔ Запрос:\n`{request_text}`\n\n💡 <b>Ответ AI-помощника по Hikka</b>:\n{answer}"
                        await message.edit(formatted_answer)
                    else:
                        formatted_answer = answer
                        await message.edit(formatted_answer)

        except aiohttp.ClientError as e:
            await message.edit(f"⚠️ Ошибка при запросе к API: {e}\n\n💡 Попробуйте поменять модель или проверить код модуля.")
            
