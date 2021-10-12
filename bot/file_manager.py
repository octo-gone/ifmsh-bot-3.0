import json
import os
from copy import deepcopy
from .config import config

save_path = os.path.join(config.get("Other", "work_dir"), "saves/")


class SaveSimple:
    def __init__(self, name):
        """Класс Сохранения. Сохраняет данные в формате json (словарь) в файловой системе."""
        self.data = None
        self.save_file = name + ".json"

    def set_data(self, data):
        """Сохраняет данные в память класса."""
        self.data = deepcopy(data)

    def load_data(self):
        """Загружает данные из файла в память. Пытается создать путь к файлу и сам файл, если файла нет."""
        try:
            os.makedirs(save_path)
        except FileExistsError:
            pass
        file_path = save_path + self.save_file
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding='utf-8') as write_file:
                json.dump({}, write_file, indent=2, ensure_ascii=False)
        with open(file_path, "r", encoding='utf-8') as read_file:
            self.data = json.loads(read_file.read())

    def save_data(self):
        """Выгружает данные из памяти класса в файл. Если данных нет вызывает ошибку."""
        if self.data is not None:
            with open(save_path + self.save_file, "w", encoding='utf-8') as write_file:
                json.dump(self.data, write_file, indent=2, ensure_ascii=False)
        else:
            raise NoDataToSave("Set data or load it first")

    def get_data(self):
        """Копирует данные из памяти класса. Если данных нет, загружает их из файла."""
        if self.data is None:
            self.load_data()
        return deepcopy(self.data)


class Save:
    def __init__(self, name: str, lock):
        """
        Продвинутый класс Сохранения. Сохраняет данные в формате json (словарь) в файловой системе.
        Блокирует доступ другим процессам к файлу. Для работы с данными требуется использовать менеджер контекста with.
        :param name: имя сохранения (имя файла)
        :param lock: блокировщик операций
        """
        self.lock = lock
        self.save_filepath = save_path + name + ".json"

    def get_data(self) -> dict:
        """
        Загружает данные из файла. Пытается создать путь к файлу и сам файл, если файла нет.
        :return: данные из файла
        """
        try:
            os.makedirs(save_path)
        except FileExistsError:
            pass
        if not os.path.exists(self.save_filepath):
            with open(self.save_filepath, "w", encoding='utf-8') as write_file:
                json.dump({}, write_file, indent=2, ensure_ascii=False)
        with open(self.save_filepath, "r", encoding='utf-8') as read_file:
            data = read_file.read()
            return json.loads(data)

    def save_data(self, data: dict):
        """Сохраняет данные в файл."""
        with open(self.save_filepath, "w", encoding='utf-8') as write_file:
            json.dump(data, write_file, indent=2, ensure_ascii=False)

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()


class NoDataToSave(Exception):
    pass

