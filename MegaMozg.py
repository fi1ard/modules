# @KeyZenD & @D4n13l3k00

import random
import logging

from telethon import types
from.. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class MegaMozgMod(loader.Module):
    strings = {
        'name': 'MegaMozg',
        'pref': '<b>[MegaMozg]</b> ',
        'need_arg': '{}Нужен аргумент',
        'tatus': '{}{}',
        'on': '{}Включён',
        'off': '{}Выключен',
        'no_messages': '{}Не найдено подходящих сообщений для ответа.'
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
        '.mozgchance <int> - Устанвоить шанс 1 к N.\n0 - всегда отвечать'
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
        if ch!= 0:
            if random.randint(0, ch)!= 0:
                return
        text = m.raw_text
        words = {random.choice(
            list(filter(lambda x: len(x) >= 3, text.split()))) for _ in ".."}
        
        # Попытка найти сообщения, на которые можно ответить
        msgs = []
        for word in words:
            try:
                async for x in m.client.iter_messages(m.chat.id, search=word):
                    if x.replies and x.replies.max_id:
                        msgs.append(x)
            except Exception as e:
                logger.warning(f"Ошибка при поиске сообщений: {e}")
        
        # Проверка наличия подходящих сообщений
        if not msgs:
            await utils.answer(m, self.strings('no_messages').format(self.strings('pref')))
            return
        
        # Выбор случайного сообщения для ответа
        try:
            replier = random.choice(msgs)
        except IndexError:
            logger.error("Неожиданный IndexError при выборе из непустого списка msgs")
            return
        
        sid = replier.id
        eid = replier.replies.max_id
        
        # Поиск ответов на выбранное сообщение
        try:
            msgs_to_reply = [x async for x in m.client.iter_messages(m.chat.id, ids=list(range(sid+1, eid+1))) if x and x.reply_to and x.reply_to.reply_to_msg_id == sid]
        except Exception as e:
            logger.warning(f"Ошибка при поиске ответов: {e}")
            return
        
        # Проверка наличия ответов
        if not msgs_to_reply:
            await utils.answer(m, self.strings('no_messages').format(self.strings('pref')))
            return
        
        # Ответ на случайный ответ
        try:
            msg_to_send = random.choice(msgs_to_reply)
            await m.reply(msg_to_send)
        except IndexError:
            logger.error("Неожиданный IndexError при выборе из непустого списка msgs_to_reply")
        except Exception as e:
            logger.error(f"Ошибка при отправке ответа: {e}")
