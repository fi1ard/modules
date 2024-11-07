import random
from telethon import types
from .. import loader, utils
from asyncio import sleep

@loader.tds
class ChipalinoMod(loader.Module):
    """Чипалино - Мод для случайных ответов и репостов в чате"""

    strings = {
        'name': 'Chipalino',
        'pref': '<b>[Чипалино]</b> ',
        'on': '{}Включён',
        'off': '{}Выключен',
        'need_arg': '{}Нужен аргумент',
        'status': '{}{}',
    }
    _db_name = 'Chipalino'

    async def client_ready(self, _, db):
        self.db = db

    async def chipalinocmd(self, m: types.Message):
        '.chipalino - Включить/выключить режим Чипалино для текущего чата'
        chat = m.chat.id
        active_chats = self.db.get(self._db_name, 'chats', [])

        if chat in active_chats:
            active_chats.remove(chat)
            await utils.answer(m, self.strings('off').format(self.strings('pref')))
        else:
            active_chats.append(chat)
            await utils.answer(m, self.strings('on').format(self.strings('pref')))

        self.db.set(self._db_name, 'chats', active_chats)

    async def chipalinochancecmd(self, m: types.Message):
        '.chipalinochance <int> - Установить шанс ответа 1 к N для текущего чата (0 - всегда отвечать)'
        args = utils.get_args_raw(m)
        if args.isdigit():
            chance = int(args)
            chat_id = m.chat.id
            chances = self.db.get(self._db_name, 'chances', {})
            chances[chat_id] = chance
            self.db.set(self._db_name, 'chances', chances)
            return await utils.answer(m, self.strings('status').format(self.strings('pref'), chance))
        return await utils.answer(m, self.strings('need_arg').format(self.strings('pref')))

    async def chipalinofreqcmd(self, m: types.Message):
        '.chipalinofreq <int> - Установить частоту самостоятельных сообщений (1 к N)'
        args = utils.get_args_raw(m)
        if args.isdigit():
            frequency = int(args)
            chat_id = m.chat.id
            frequencies = self.db.get(self._db_name, 'frequencies', {})
            frequencies[chat_id] = frequency
            self.db.set(self._db_name, 'frequencies', frequencies)
            return await utils.answer(m, self.strings('status').format(self.strings('pref'), frequency))
        return await utils.answer(m, self.strings('need_arg').format(self.strings('pref')))

    async def watcher(self, m: types.Message):
        if not isinstance(m, types.Message) or not m.chat:
            return

        chat_id = m.chat.id
        active_chats = self.db.get(self._db_name, 'chats', [])
        if chat_id not in active_chats:
            return

        # Получаем шанс ответа и частоту самостоятельных сообщений для текущего чата
        chances = self.db.get(self._db_name, 'chances', {})
        chance = chances.get(chat_id, 0)

        frequencies = self.db.get(self._db_name, 'frequencies', {})
        frequency = frequencies.get(chat_id, 0)

        # Случайное сообщение из истории чата
        msgs = []
        async for message in m.client.iter_messages(m.chat.id, limit=50):
            msgs.append(message)
        if not msgs:
            return

        random_message = random.choice(msgs)

        # Проверка на самостоятельное сообщение
        if frequency > 0 and random.randint(1, frequency) == 1:
            await self.send_random_message(m.client, m.chat.id, random_message)

        # Проверка на ответное сообщение
        elif chance == 0 or random.randint(1, chance) == 1:
            await self.send_random_message(m.client, m.chat.id, random_message, reply_to=m)

    async def send_random_message(self, client, chat_id, message, reply_to=None):
        """
        Функция для отправки случайного сообщения.
        """
        if message.text:  # Если это текстовое сообщение
            await client.send_message(chat_id, message.text, reply_to=reply_to)
        elif message.photo:  # Если это фото
            await client.send_file(chat_id, message.photo, caption=message.text, reply_to=reply_to)
        elif message.sticker:  # Если это стикер
            await client.send_file(chat_id, message.sticker, reply_to=reply_to)
        elif message.voice:  # Если это голосовое сообщение
            await client.send_file(chat_id, message.voice, reply_to=reply_to)
        elif message.document:  # Если это другой файл
            await client.send_file(chat_id, message.document, caption=message.text, reply_to=reply_to)

    async def independent_message_sender(self):
        """
        Запуск самостоятельной отправки случайного сообщения из истории чата
        в любое время с учетом установленной частоты.
        """
        while True:
            active_chats = self.db.get(self._db_name, 'chats', [])
            for chat_id in active_chats:
                frequencies = self.db.get(self._db_name, 'frequencies', {})
                frequency = frequencies.get(chat_id, 0)
                if frequency > 0 and random.randint(1, frequency) == 1:
                    msgs = []
                    async for message in self.client.iter_messages(chat_id, limit=50):
                        msgs.append(message)
                    if msgs:
                        random_message = random.choice(msgs)
                        await self.send_random_message(self.client, chat_id, random_message)
            await sleep(10)  # Задержка между проверками, чтобы не нагружать чат
