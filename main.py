import os
import time
import requests
import datetime

# Читаем переменные окружения
TELEGRAM_TOKEN = "6813293461:AAEw_dZhCDUwr9pOjz40blZd4lL4yl6wEs4"  # Токен вашего Telegram-бота
TELEGRAM_CHAT_ID = "782821990"  # ID чата/пользователя
MONITOR_URL = "https://coonlink.fun"  # URL, который проверяем
CHECK_INTERVAL = 30  # Интервал проверки в секундах (число, не строка)

# Храним, "был ли сайт недоступен" на предыдущей проверке
site_is_down = None  # None = еще не знаем, True = упал, False = работает


def send_telegram_message(text: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Не заданы TELEGRAM_TOKEN или TELEGRAM_CHAT_ID!")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        resp = requests.post(url,
                             data={
                                 "chat_id": TELEGRAM_CHAT_ID,
                                 "text": text
                             })
        if resp.status_code == 200:
            print(f"Сообщение отправлено: {text}")
        else:
            print(f"Ошибка при отправке: {resp.text}")
    except Exception as e:
        print(f"Ошибка при запросе к Telegram API: {str(e)}")


def check_site():
    global site_is_down
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        r = requests.get(MONITOR_URL, timeout=5)
        if r.status_code == 200:
            # Сайт доступен
            if site_is_down is True:
                # Был «упавшим», а теперь ответил 200 — сообщим, что восстановился
                msg = (f"✅ Сайт {MONITOR_URL} снова доступен!\n"
                       f"Время: {time_now}")
                send_telegram_message(msg)
            site_is_down = False
            print(
                f"[OK] {MONITOR_URL} доступен (код={r.status_code}) — {time_now}"
            )
        else:
            # Код не 200 — считаем, что сайт недоступен
            if site_is_down is False or site_is_down is None:
                # Был «работающим» (или первое измерение) — отправляем оповещение об ошибке
                msg = (f"⚠ Сайт {MONITOR_URL} ответил кодом {r.status_code}\n"
                       f"Время: {time_now}")
                send_telegram_message(msg)
            site_is_down = True
            print(
                f"[FAIL] {MONITOR_URL} ответил кодом {r.status_code} — {time_now}"
            )

    except Exception as e:
        # Ловим любые сетевые ошибки, таймаут и т.п.
        if site_is_down is False or site_is_down is None:
            msg = (f"❌ Сайт {MONITOR_URL} недоступен:\n"
                   f"{str(e)}\n"
                   f"Время: {time_now}")
            send_telegram_message(msg)
        site_is_down = True
        print(f"[ERROR] {MONITOR_URL} недоступен: {str(e)} — {time_now}")


def main():
    while True:
        check_site()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
