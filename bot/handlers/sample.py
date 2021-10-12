import bot.file_manager as fm
from bot import senders


def run(data, save_lock):
    save = fm.Save("sample", save_lock)
    # ваши операции ниже

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

    file = "./resources/images/belyash.jpg"
    message = "Message"
    # отправить файл
    senders.send_file(senders.get_api(), int(data["peer_id"]), file, message)
    # отправить фотографию
    senders.send_photo(senders.get_api(), int(data["peer_id"]), file, message)
    # отправить файл
    senders.send_chat_msg(senders.get_api(), int(data["peer_id"]), message)
