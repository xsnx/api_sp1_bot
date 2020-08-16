import os
import requests
import telegram
import time
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.WARNING, filename='app.log',
                    format='%(asctime)s - %(message)s')

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    try:
        homework_name = homework.get('homework_name')
    except Exception as e:
        logging.exception(f"Exception - {e}")
        print(f'Ошибка homework: {e}')
    if homework['status'] != 'approved':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        logging.error('get_homework_statuses -current_timestamp is None:')
        current_timestamp = 0
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    data = {
        'from_date': current_timestamp,
    }
    url = "https://praktikum.yandex.ru/api/user_api/homework_statuses/"
    try:
        homework_statuses = requests.get(f'{url}', headers=headers, params=data)
    except Exception as e:
        logging.exception(f"Exception - {e}")
        print(f'Ошибка запроса: {e}')
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут

        except Exception as e:
            logging.exception(f"Exception - {e}")
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
