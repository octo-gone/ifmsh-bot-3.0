import vk_api.vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from . import senders, database as db
from .plugins import sample
from .config import config

import multiprocessing as mp


class Lock:
    def __init__(self, lock):
        self.lock = lock

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()


db.connect(str(config.get("Other", "db_name")))


class Bot:
    def __init__(self):
        self.vk = vk_api.VkApi(token=config.get("Credentials", "vk_api_token"))
        self.vk_api = self.vk.get_api()

        self.group_id = int(config.get("Credentials", "group_id"))
        self.long_poll = VkBotLongPoll(self.vk, self.group_id)

    def start(self):
        lock = Lock(mp.RLock())
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat:
                message = event.object.message
                chat_id = str(event.chat_id)
                from_id = message['from_id']
                message["chat_id"] = event.chat_id

                chat = db.Chat.objects(chat_id=int(chat_id))
                if not chat:
                    chat = db.Chat(chat_id=int(chat_id))
                    chat.save()
                else:
                    chat = chat[0]

                user = db.User.objects(user_id=int(from_id))
                if not user:
                    name = self.get_user_name(from_id)
                    user = db.User(user_id=int(from_id), first_name=name[0], last_name=name[1])
                    user.save()
                else:
                    user = user[0]

                # plugins
                mp.Process(target=sample.run, args=(message, lock, chat, user)).start()

    def get_user_name(self, user_id):
        user_data = self.vk_api.users.get(user_id=user_id)[0]
        return user_data['first_name'], user_data['last_name']
