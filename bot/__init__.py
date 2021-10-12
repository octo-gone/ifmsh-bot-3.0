import vk_api.vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from . import utils, senders, file_manager as fm
from .config import config
from .handlers import sample

import multiprocessing as mp


class Bot:
    def __init__(self):
        self.vk = vk_api.VkApi(token=config.get("Credentials", "vk_api_token"))
        self.vk_api = self.vk.get_api()

        self.data_saves = fm.SaveSimple("saves")
        self.data = self.data_saves.get_data()
        if "chats" not in self.data:
            self.data["chats"] = {}

        self.group_id = int(config.get("Credentials", "group_id"))
        self.long_poll = VkBotLongPoll(self.vk, self.group_id)

    def save_data(self):
        self.data_saves.set_data(self.data)
        self.data_saves.save_data()

    def start(self):
        save_lock = mp.RLock()
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat:
                message = event.object.message
                chat_id = str(event.chat_id)
                from_id = message['from_id']
                message["chat_id"] = event.chat_id

                if chat_id not in self.data["chats"]:
                    self.data["chats"][chat_id] = {"users": {}, "chat": {}}

                chat_data = self.data["chats"][chat_id]

                if str(from_id) not in chat_data["users"]:
                    chat_data["users"][str(from_id)] = {}

                # plugins
                mp.Process(target=sample.run, args=(self.vk_api, message, save_lock)).start()

                self.save_data()

    def get_user_name(self, user_id):
        user_data = self.vk_api.users.get(user_id=user_id)[0]
        return user_data['first_name'] + " " + user_data['last_name']
