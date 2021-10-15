
# IFMSH Bot Mongo

[![made-with-python](https://img.shields.io/badge/Made%20with-Python_3.8-1f425f.svg)](https://www.python.org/)

Данный проект представляет собой шаблон бота для беседы VK на Python 3.8 с использованием базы данных MongoDB. 

## Запуск бота

Для запуска будет использоваться файл _main.py_. Перед запуском требуется установить все модули Python из _requirements.txt_, 
выполнив в командной строке следующую команду:

```commandline
pip install -r requirements.txt
```

Также для работы бота требуется API токен. Токен сообщества можно получить создав сообщество и зайдя в настройках в _Работа с API_. 
После генерации токена его нужно настроить. Данный шаблон работает стабильно на версии API 5.126 используя Long Poll API. 
Токен и идентификатор сообщества требуется указать в файле _config.ini_. 
Если файл не создан запустите скрипт _main.py_.

Остается лишь указать в конфигурационном файле путь к рабочей директории в виде полного пути или относительного. 
В _config.ini_ можно не указывать _standalone_token_ и _python_.

## Описание плагина

Для анализа сообщений достаточно создать Python-файл в модуле _bot/plugins_
со следующей структурой. Пример: _bot/plugins/sample.py_

```python
import bot.database as db
from mongoengine import Document, IntField, StringField, ReferenceField, DateTimeField
from bot import senders



def run(data, lock, chat, user):
    # ваши операции ниже
```

После создания остается импортировать в _bot/\_\_init\_\_.py_ плагин и указать запуск процесса в главном цикле.

```python
# plugins
mp.Process(target=sample.run, args=(message, save_lock, chat, user)).start()
```

В функцию _run_ передается сообщение, блокировщик, объекты чата и пользователя из базы данных.

### DataBase

**MongoDB** - система управления базами данных, для работы с БД потребуется 
[скачать и установить](https://www.mongodb.com/try/download/community) сервер MongoDB и запустить его. 
Дополнительно потребуется создать папку _data_ в основной директории бота.

```
"<путь к серверу>\bin\mongod" --dbpath "<путь к проекту>\data"
``` 

База данных состоит из коллекций (разделов) и документов внутри коллекций (записей). 

Библиотека _database_ предоставляет разработчику доступ к двум базовым коллекциям: пользователь и чат. 
Каждый класс определяет коллекцию в базе данных - **модель**. В классе с помощью дескрипторов (классов, которые определяют, как данные
сохраняются и отдаются) описываются поля к документу.

```python
class Chat(Document):
    chat_id = IntField(required=True, unique=True)

class User(Document):
    user_id = IntField(required=True, unique=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
```

> Функции \_\_str\_\_ и \_\_repr\_\_ позволяют выводить данные в консоль в читаемом для человека формате

#### Работа с данными

Для создания нового документа требуется инициализировать класс модели, передав в него данные или после установив с помощью присваивания.

```python
usr = User(user_id=123456, first_name="Ваня", last_name="Ванов")
```

Данный документ не сохраняет в БД, так как является лишь структурой в Python. Для сохранения достаточно использовать метод _save_.

```python
usr.save()
```

Кроме создания можно получить данные из коллекции, здесь также потребуется использовать модель, но вместо инициализации будет
проходить работа с атрибутом/методом _objects_. Указав в нем поле из модели можно получить определенный набор документов, например,
с указанным идентификатором. _objects_ возвращает список документов, даже если документ один.

```python
all_users_docs = User.objects()
users_docs_with_id_123456 = User.objects(user_id=123456) 

if users_docs_with_id_123456:
    usr = users_docs_with_id_123456[0]
```

#### Создание своих коллекций и данных в БД

Для создания коллекции, аналогично библиотеке database, потребуется создать класс. Внутри модели могут описываться любые 
данные и зависимости, для большей информации обратитесь к [документации mongoengine](https://mongoengine-odm.readthedocs.io/index.html).

```python
import bot.database as db
from mongoengine import Document, IntField, StringField, ReferenceField, DateTimeField

class SimpleMessage(Document):
    user = IntField(required=True)
    chat = IntField(required=True)
    message = StringField()

class Message(Document):
    user = ReferenceField(db.User, required=True)
    chat = ReferenceField(db.Chat, required=True)
    timestamp = DateTimeField()
    message = StringField()
```

Если коллекция имеет зависимость от пользователей или чата, то рекомендуется описывать зависимые поля.

### Lock

В связи с многопоточной работой бота для точной работы с данными потребуется блокировщик, он не дает другим процессам
работать с базой данных, следовательно, все полученные данные при включенном блокировщике будут свежими. 

Для работы требуется включить блокировщик `lock.acquire()` и затем выключить `lock.release()`,
либо воспользоваться конструкцией _with-as_. Пока операции внутри контекстного менеджера не будут выполнены блокировщик не
выключится. Желательно использовать блокировщик только при работе с данными.

```python
lock.acquire()
# взаимодействие с БД
lock.release()

with lock:
    # взаимодействие с БД
```

### Senders

Библиотека _senders_ позволит отправлять сообщения, файлы и фотографии в беседу и пользователям. Для работы
требуется отправить API ВК, идентификатор беседы (или пользователя) и сообщение с файлом. Для фото и файла не требуется
указывать сообщение. API можно получить с помощью функции `senders.get_api()`.

```python
file = "./resources/images/belyash.jpg"
message = "Message"
# отправить сообщение
senders.send_chat_msg(senders.get_api(), chat.chat_id, message)
# отправить файл
senders.send_file(senders.get_api(), chat.chat_id, file, message)
# отправить фотографию
senders.send_photo(senders.get_api(), chat.chat_id, file, message)
```

## Структура сообщения и других типов данных

```python
message = {
    "chat_id": int,
    "date": int,
    "from_id": int,
    "peer_id": int,
    "text": str,
    "conversation_message_id": int,
    "fwd_messages": [message, ...],
    "reply_message": reply_message,
    "attachments": [attachment, ...]
}

reply_message = {
    "date": int,
    "from_id": int,
    "conversation_message_id": int,
    "peer_id": int,
    "id": int,
    "attachments": [attachment, ...]
}

attachments = {
    "type": "photo" | "audio" | "audio_message" | ...,
    # description of attachment types, only one per attachment
    "photo" : {
        "id": int,
        "owner_id": int,
        "date": int,
        "sizes": [
            {
                "height": int,
                "width": int,
                "type": "s" | "m" | "x" | "o" | "p" | "q" | "r" | ...,
                "url": str
            }, ...
        ],
        "text": str
    },
    "audio" : {
        "id": int,
        "owner_id": int,
        "artist": str,
        "title": str,
        "duration": int,
        "is_explicit": bool,
        "track_code": str,
        "date": int,
        "sizes": [
            {
                "height": int,
                "width": int,
                "type": "s" | "m" | "x" | "o" | "p" | "q" | "r" | ...,
                "url": str
            }, ...
        ]
    },
    "audio_message" : {
        "id": int,
        "owner_id": int,
        "duration": int,
        "waveform": [int, int, ...],
        "link_ogg": str,
        "link_mp3": str
    },
}
```
