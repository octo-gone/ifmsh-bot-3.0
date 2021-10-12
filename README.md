
# IFMSH Bot 3.0

[![made-with-python](https://img.shields.io/badge/Made%20with-Python_3.9.5-1f425f.svg)](https://www.python.org/)

Данный проект представляет собой шаблон бота для беседы VK на Python 3.8. 

## Запуск бота

Для запуска будет использоваться файл _main.py_. Перед запуском требуется установить все требуемые модули Python, 
выполнив в командной строке следующую команду:

```commandline
pip install -r requirements.txt
```

Также для работы бота требуется API токен. Токен сообщества можно получить создав сообщество и зайдя в настройках в _Работа с API_. 
После генерации токена его нужно настроить. Данный шаблон работает стабильно на версии API 5.126 используя Long Poll API. 
Данный токен, как и идентификатор сообщества требуется указать в файле _config.ini_. 
Если файл не создан запустите скрипт _main.py_.

Последним этапом является указание в конфигурационном файле путь к рабочей директории в виде полного пути или относительного. 
В _config.ini_ можно не указывать _standalone_token_ и _python_.

## Описание плагина

Для анализа сообщений достаточно создать Python-файл в модуле _bot/handlers_
со следующей структурой. Пример: _bot/handlers/sample.py_

```python
import bot.file_manager as fm
from bot import senders


def run(api, data, save_lock):
    save = fm.Save("<имя файла сохранения>", save_lock)
    # ваши операции ниже
```

После создания остается импортировать в _bot/\_\_init\_\_.py_ плагин и указать запуск процесса в главном цикле.

```python
# plugins
mp.Process(target=sample.run, args=(self.vk_api, message, save_lock)).start()
```

### File Manager

Библиотека _file_manager_ позволяет сохранять данные в формате _json_. Для работы
сохранения требуется блокировщик, который не позволяет работать с файлами другим процессам.

Для работы с данными требуется включить блокировщик `save_lock.acquire()` и затем выключить `save_lock.release()`,
либо использовать конструкцию _with-as_. Пока операции внутри контекстного менеджера не будут выполнены блокировщик не
выключится.

```python
with save:
    # получить данные
    save_data = save.get_data()

with save:
    # сохранить данные
    save.save_data(save_data)

with save:
    # сохранить или получить данные
    save_data = save.get_data()
    # операции над данными
    save.save_data(save_data)
```

### Senders

Библиотека _senders_ в дальнейшем позволит отправлять сообщения, файлы и фотографии в беседу и пользователям. Для работы
требуется отправить API ВК, идентификатор беседы (или пользователя) и сообщение с файлом. Для фото и файла не требуется
указывать сообщение.

```python
file = "./resources/images/belyash.jpg"
message = "Message"
# отправить файл
senders.send_file(api, int(data["peer_id"]), file, message)
# отправить фотографию
senders.send_photo(api, int(data["peer_id"]), file, message)
# отправить файл
senders.send_chat_msg(api, int(data["peer_id"]), message)
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