import bot.database as db
from mongoengine import Document, IntField, StringField, ReferenceField, DateTimeField
from bot import senders
from datetime import datetime


# models
class Message(Document):
    user = ReferenceField(db.User, required=True)
    chat = ReferenceField(db.Chat, required=True)
    timestamp = DateTimeField()
    message = StringField()

    def __str__(self):
        return f"<Message {self.timestamp}: '{self.message}' ({self.user})>"

    def __repr__(self):
        return f"<Message {self.timestamp}: '{self.message}' ({self.user})>"


class LastMessage(Document):
    user = ReferenceField(db.User, required=True)
    chat = ReferenceField(db.Chat, required=True)
    timestamp = DateTimeField()
    message = StringField()

    def __str__(self):
        return f"<LastMessage {self.timestamp}: '{self.message}' ({self.user})>"

    def __repr__(self):
        return f"<LastMessage {self.timestamp}: '{self.message}' ({self.user})>"

    meta = {'indexes': [{'fields': ('user', 'chat'), 'unique': True}]}


def run(data, lock, chat, user):
    ts = datetime.fromtimestamp(data['date'])
    msg = Message(user=user, chat=chat, timestamp=ts, message=data["text"])

    msg.save()

    with lock:
        last_msgs = LastMessage.objects(user=user, chat=chat)
        if last_msgs and last_msgs[0].timestamp < ts:
            last_msg = last_msgs[0]
            last_msg.timestamp = ts
            last_msg.message = data["text"]
        else:
            last_msg = LastMessage(user=user, chat=chat, timestamp=ts, message=data["text"])
        last_msg.save()

    senders.send_chat_msg(senders.get_api(), chat.chat_id, f"{len(Message.objects(user=user, chat=chat))} msg in memory")
