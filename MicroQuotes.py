import random
from telethon import types
from .. import loader, utils

@loader.tds
class MajorPodzalupenkoMod(loader.Module):
    """Майор Подзалупенко - Мод для случайных ответов в чате"""

    strings = {
        'name': 'MajorPodzalupenko',
        'pref': '<b>[Майор Подзалупенко]</b> ',
        'on': '{}Включён',
        'off': '{}Выключен',
        'need_arg': '{}Нужен аргумент',
        'status': '{}{}',
    }
    _db_name = 'MajorPodzalupenko'

    async def client_ready(self, _, db):
        self.db = db

    @staticmethod
    def str2bool(v):
        return v.lower() in ("yes", "y", "ye", "yea", "true", "t", "1", "on", "enable", "start", "run", "go", "да")

    async def podzalupencmd(self, m: types.Message):
        '.podzalupen - Включить/выключить режим дурачка для текущего чата (Майор Подзалупенко)'
        chat = m.chat.id
        active_chats = self.db.get(self._db_name, 'chats', [])

        if chat in active_chats:
            active_chats.remove(chat)
            await utils.answer(m, self.strings('off').format(self.strings('pref')))
        else:
            active_chats.append(chat)
            await utils.answer(m, self.strings('on').format(self.strings('pref')))

        self.db.set(self._db_name, 'chats', active_chats)

    async def podzalupenchancecmd(self, m: types.Message):
        '.podzalupenchance <int> - Установить шанс ответа 1 к N для текущего чата (0 - всегда отвечать) (Майор Подзалупенко)'
        args = utils.get_args_raw(m)
        if args.isdigit():
            chance = int(args)
            chat_id = m.chat.id
            chances = self.db.get(self._db_name, 'chances', {})
            chances[chat_id] = chance
            self.db.set(self._db_name, 'chances', chances)
            return await utils.answer(m, self.strings('status').format(self.strings('pref'), chance))
        return await utils.answer(m, self.strings('need_arg').format(self.strings('pref')))

    async def podzalupenfreqcmd(self, m: types.Message):
        '.podzalupenfreq <int> - Установить частоту самостоятельных сообщений (1 к N, 0 - всегда отправлять) (Майор Подзалупенко)'
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
            if message.text:
                msgs.append(message.text)
        if not msgs:
            return

        random_message = random.choice(msgs)

        # Проверка на самостоятельное сообщение
        if frequency > 0 and random.randint(1, frequency) == 1:
            await m.client.send_message(m.chat.id, random_message)
        elif chance == 0 or random.randint(1, chance) == 1:
            await m.reply(random_message)
