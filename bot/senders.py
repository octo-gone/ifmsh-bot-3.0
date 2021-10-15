import vk_api.vk_api
from vk_api.utils import get_random_id
from vk_api.upload import VkUpload

from .config import config


def get_api():
    """Получить VK API напрямую"""
    vk = vk_api.VkApi(token=config.get("Credentials", "vk_api_token"))
    api = vk.get_api()
    return api


def send_msg(api, send_id, message, **kwargs):
    """
    Отправить сообщение пользователю
    :param api: VK API
    :param send_id: идентификатор чата
    :param message: сообщение
    :param kwargs: ключевые аргументы
    """
    api.messages.send(peer_id=send_id,
                      message=message,
                      random_id=get_random_id(),
                      **kwargs)


def send_chat_msg(api, chat_id, message, **kwargs):
    """
    Отправить сообщение в беседу
    :param api: VK API
    :param chat_id: идентификатор беседы
    :param message: сообщение
    :param kwargs: ключевые аргументы
    """
    api.messages.send(chat_id=chat_id,
                      message=message,
                      random_id=get_random_id(),
                      **kwargs)


def upload_photo(upload, photo):
    response = upload.photo_messages(photo)[0]

    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    return owner_id, photo_id, access_key


def send_file(api, peer_id, file_path, message=""):
    """
    Отправить файл, в том числе и файл с анимацией (gif)
    :param api: VK API
    :param peer_id: идентификатор беседы или чата
    :param file_path: путь к файлу
    :param message: сообщение
    """
    upload = VkUpload(api)
    if not isinstance(file_path, (tuple, list, set)):
        file_path = [file_path]
    attachment = ""
    for file in list(file_path):
        d = upload.document_message(file, peer_id=peer_id, title=file[:-4])["doc"]["url"]
        attachment += "," + d[15:d.index("?")]
    send_msg(api, send_id=peer_id, message=message, attachment=attachment[1:])


def send_photo(api, peer_id, file_path, message=""):
    """
    Отправить фотографию
    :param api: VK API
    :param peer_id: идентификатор беседы или чата
    :param file_path: путь к файлу
    :param message: сообщение
    """
    upload = VkUpload(api)
    if not isinstance(file_path, (tuple, list, set)):
        file_path = [file_path]
    attachment = ""
    for file in file_path:
        owner_id, photo_id, access_key = upload_photo(upload, file)
        d = f'photo{owner_id}_{photo_id}_{access_key}'
        attachment += "," + d
    send_msg(api, send_id=peer_id, message=message, attachment=attachment[1:])
