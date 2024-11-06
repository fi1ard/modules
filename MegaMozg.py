import random

from telethon import types

from .. import loader, utils


@loader.tds
class MegaMozgMod(loader.Module):
    strings = {
        'name': 'MegaMozg',
        'pref': '<b>[MegaMozg]</b> ',
        'need_arg': '{}Нужен аргумент',
        'status': '{}{}',
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
        '.mozg <on/off/...> - Переключить режим дурачка в чате'
        args = utils.get_args_raw(m)
        if not m.chat:
            return
        chat = m.chat.id
        if self.str2bool(args):
            chats: list = self.db.get(self._db_name, 'chats', [])
            chats.append(chat)
            chats = list(set(chats))
            self.db.set(self._db_name, 'chats', chats)
            return await utils.answer(m, self.strings('on').format(self.strings('pref')))
        chats: list = self.db.get(self._db_name, 'chats', [])
        try:
            chats.remove(chat)
        except:
            pass
        chats = list(set(chats))
        self.db.set(self._db_name, 'chats', chats)
        return await utils.answer(m, self.strings('off').format(self.strings('pref')))

    async def mozgchancecmd(self, m: types.Message):
        '.mozgchance <int> - Установить шанс 1 к N.\n0 - всегда отвечать'
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
        ch = self.db.get(self._db_name, 'chance', 0)
        if ch != 0:
            if random.randint(0, ch) != 0:
                return
        text = m.raw_text
        words_list = [word for word in text.split() if len(word) >= 3]
        if not words_list:
            return
        # Берем два случайных слова из списка
        words = set()
        for _ in range(2):
            words.add(random.choice(words_list))
        msgs = []
        for word in words:
            async for x in m.client.iter_messages(m.chat.id, search=word):
                if x.replies and x.replies.max_id:
                    msgs.append(x)
        if not msgs:
            return
        replier = random.choice(msgs)
        sid = replier.id
        eid = replier.replies.max_id
        if not eid:
            return
        reply_msgs = []
        async for x in m.client.iter_messages(
                m.chat.id,
                ids=list(range(sid + 1, eid + 1))):
            if x and x.reply_to and x.reply_to.reply_to_msg_id == sid:
                reply_msgs.append(x)
        if not reply_msgs:
            return
        msg = random.choice(reply_msgs)
        await m.reply(msg)
