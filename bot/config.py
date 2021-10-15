import os
import configparser


class NoConfigFound(Exception):
    pass


config = configparser.ConfigParser()

if not os.path.exists("./config.ini"):
    config["Credentials"] = {
        "vk_api_token": "-><-",
        "standalone_token": "-><-",
        "group_id": "-><-"
    }
    config["Other"] = {
        "db_name": "ifmsh-bot",
        "python": "-><-",
        "work_dir": os.path.realpath(os.path.join(os.getcwd() + "\\..\\"))
    }
    with open('./config.ini', 'w') as configfile:
        config.write(configfile)
    raise NoConfigFound("Config file 'config.ini' was generated, please enter auth data into it")

config.read("./config.ini")
