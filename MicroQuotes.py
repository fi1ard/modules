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
        'need_arg': '{}Нужен аргумент',
        'status': '{}{}',
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
        if chat not in chats:
            chats.append(chat)
            self.db.set(self._db_name, 'chats', chats)
        return await utils.answer(m, self.strings('on').format(self.strings('pref')))

    async def mozgchancecmd(self, m: types.Message):
        '.mozgchance <int> - Установить шанс 1 к N. 0 - всегда отвечать'
        args: str = utils.get_args_raw(m)
        if args.isdigit():
            self.db.set(self._db_name, 'chance', int(args))
            return await utils.answer(m, self.strings('status').format(self.strings('pref'), args))
        return await utils.answer(m, self.strings('need_arg').format(self.strings('pref')))

    async def watcher(self, m: types.Message):
        if not isinstance(m, types.Message):
            return
        if m.sender_id == (await m.client.get_me()).id or not m.chat:
            return
        if m.chat.id not in self.db.get(self._db_name, 'chats', []):
            return

        # Получаем старые сообщения чата (можно изменить лимит, если нужно больше сообщений)
        msgs = []
        async for message in m.client.iter_messages(m.chat.id, limit=50):  # Получаем последние 50 сообщений
            if message.text:  # Проверка на None
                msgs.append(message.text)

        if not msgs:
            return  # Если сообщений нет, ничего не отправляем

        # Выбираем случайное сообщение из истории чата
        random_message = random.choice(msgs)

        # Отправляем выбранное сообщение в ответ
        await m.reply(random_message)
