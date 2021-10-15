from mongoengine import connect, Document
from mongoengine import IntField, StringField


class Chat(Document):
    chat_id = IntField(required=True, unique=True)

    def __str__(self):
        return f"<Chat {self.chat_id}>"

    def __repr__(self):
        return f"<Chat {self.chat_id}>"


class User(Document):
    user_id = IntField(required=True, unique=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)

    def __str__(self):
        return f"<User {self.user_id} ({self.first_name} {self.last_name})>"

    def __repr__(self):
        return f"<User {self.user_id} ({self.first_name} {self.last_name})>"

