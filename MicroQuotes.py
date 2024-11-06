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
        
        # Получаем id чата
        chat_id = m.chat.id
        # Получаем список чатов из базы данных
        chats: list = self.db.get(self._db_name, 'chats', [])
        
        # Если чат не включен в список, прекращаем выполнение
        if chat_id not in chats:
            return

        # Получаем шанс из базы данных
        ch = self.db.get(self._db_name, 'chance', 0)
        if ch != 0:
            if random.randint(0, ch) != 0:
                return
        
        # Получаем последние 500 сообщений из чата
        msgs = []
        async for message in m.client.iter_messages(m.chat.id, limit=500):  # Получаем последние 500 сообщений
            if message.text and isinstance(message.text, str) and message.text.strip():  # Проверка на None и пустые строки
                msgs.append(message.text)

        # Если сообщений нет, ничего не отправляем
        if not msgs:
            return

        # Выбираем случайное сообщение из истории чата
        random_message = random.choice(msgs)

        # Отправляем выбранное сообщение в ответ
        try:
            if random_message:  # Проверяем, что выбранное сообщение не пустое
                await m.reply(random_message)
        except Exception as e:
            # Логируем ошибку, если возникла ошибка при отправке сообщения
            print(f"Ошибка при отправке сообщения: {e}")
