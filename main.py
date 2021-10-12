from bot import Bot
import requests
import time


if __name__ == '__main__':
    for restart in range(100):
        try:
            bot = Bot()
            bot.start()
        except requests.exceptions.ConnectionError as exception:
            print(exception)
            time.sleep(100)
            continue
