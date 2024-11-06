import random
from telethon import types
from .. import loader, utils

@loader.tds
class MegaMozgMod(loader.Module):
    strings = {
        'name': 'MegaMozg',
        'pref': '<b>[MegaMozg]</b> ',
        'on': '{}Включён',
        'off': '{}Выключен',
    }
    _db_name = 'MegaMozg'

    async def client_ready(self, _, db):
        self.db = db

    @staticmethod
    def str2bool(v):
        return v.lower() in ("yes", "y", "ye", "yea", "true", "t", "1", "on", "enable", "start", "run", "go", "да")

    async def mozgcmd(self, m: types.Message):
        '.mozg - Включить режим дурачка'
        if not m.chat:
            return
        chat = m.chat.id
        chats: list = self.db.get(self._db_name, 'chats', [])
        chats.append(chat)
        chats = list(set(chats))  # Убираем дубли
        self.db.set(self._db_name, 'chats', chats)
        return await utils.answer(m, self.strings('on').format(self.strings('pref')))

    async def watcher(self, m: types.Message):
        if not isinstance(m, types.Message):
            return
        if m.sender_id == (await m.client.get_me()).id or not m.chat:
            return
        if m.chat.id not in self.db.get(self._db_name, 'chats', []):
            return

        # Получаем все сообщения в чате
        msgs = []
        async for message in m.client.iter_messages(m.chat.id, limit=50):  # Ограничиваем 50 последними сообщениями
            if message.text:
                msgs.append(message.text)

        if not msgs:
            return  # Если нет сообщений, выходим

        # Выбираем случайное сообщение
        random_message = random.choice(msgs)

        # Ответ на текущее сообщение случайным образом выбранным старым сообщением
        await m.reply(random_message)
