import asyncio
import logging
import re
import traceback
import sys
from exchangelib import Account, Credentials, Message, Mailbox, Configuration

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_errors.log', encoding='utf-8', mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
logger.info("=== БОТ ДЛЯ MAX — ФИНАЛЬНАЯ ВЕРСИЯ С УЛУЧШЕННОЙ ВАЛИДАЦИЕЙ ===")

try:
    from maxapi import Bot, Dispatcher, F
    from maxapi.types import BotStarted, Command, MessageCreated, MessageCallback
    logger.info("✅ maxapi успешно импортирован")
except Exception as e:
    logger.critical(f"❌ Ошибка импорта: {e}")
    logger.critical(traceback.format_exc())
    sys.exit(1)

# ================= НАСТРОЙКИ =================
MAX_BOT_TOKEN = "f9LHodD0cOJqiWIZloj02nN0_USdrs2vZf6SU5enPn27SWmR432VOox3hZm_xOw1x1_tFcDVW0rBZLz8CdEE"
YOUR_EMAIL = "s.volkov@caterinburg.ru"
YOUR_PASSWORD = "Vo2024sE0810"
# ===== ПОДПИСЬ ТОЧНО КАК В РУЧНОМ ПИСЬМЕ =====

SIGNATURE = """--
С уважением,
Сергей Волков
Управляющий
117198, г. Москва, ул. Миклухо-Маклая, 6, РУДН
т. сот.: +7 (961) 388-84-82
эл.почта: s.volkov@caterinburg.ru

www.caterinburg.ru
https://vk.com/caterinburg"""

def send_email_via_exchange(car_number: str, point_key: str):
    point_addresses = {
        "mm6": "Миклухо-Маклая, д.6",      # исправлено: д.6, а не д.б
        "mm10k2": "Миклухо-Маклая, д.10к2",
        "ordzhonikidze": "Орджоникидзе, д.3",
    }
    address = point_addresses.get(point_key, "Неизвестная точка")
    credentials = Credentials(username=YOUR_EMAIL, password=YOUR_PASSWORD)
    try:
        account = Account(primary_smtp_address=YOUR_EMAIL, credentials=credentials, autodiscover=True, access_type='delegate')
    except Exception:
        config = Configuration(server='owa.ekdekb.ru', credentials=credentials)
        account = Account(primary_smtp_address=YOUR_EMAIL, config=config, autodiscover=False, access_type='delegate')
    
    # Формируем тело письма в точности как на скриншоте
    body = f"Прошу пропустить машину для разгрузки на {address}.\n{car_number}\nЗаранее спасибо.\n\n{SIGNATURE}"
    
    msg = Message(
        account=account,
        subject=f'Заявка на пропуск {car_number}',
        body=body,
        to_recipients=[Mailbox(email_address=YOUR_EMAIL)]  # потом замените на bp@pfur.ru
    )
    msg.send()
    logger.info(f"✅ Письмо отправлено для {car_number} (на {YOUR_EMAIL})")

MAPS = {
    "mm6": "https://i.ibb.co/0Rckvcvf/6.png",
    "mm10k2": "https://i.ibb.co/Zz0PP6fY/10-2.png",
    "ordzhonikidze": "https://i.ibb.co/nMsbqc0X/image.png",
}

CONTACTS = {
    "mm6": "👥 *Контакты склада (Миклухо-Маклая, д.6):*\n• Кладовщик Наталья: +79256050358\n• Грузчик Сергей: +79269552848",
    "mm10k2": "👥 *Контакты склада (Миклухо-Маклая, д.10к2):*\n• Администратор Илаха: +79778320200\n• Зав. производства Анна: +79663171768",
    "ordzhonikidze": "👥 *Контакты склада (Орджоникидзе, д.3):*\n• Администратор Екатерина: +79171253314",
}

def is_valid_plate(text: str) -> bool:
    """Проверяет, является ли строка корректным российским госномером."""
    original = text
    # Очищаем: убираем пробелы, дефисы, приводим к верхнему регистру
    cleaned = text.replace(" ", "").replace("-", "").upper()
    # Регулярное выражение для российских номеров:
    # 1 буква, 3 цифры, 2 или 3 буквы, 2 или 3 цифры (код региона)
    pattern = r"^[АВЕКМНОРСТУХ]\d{3}[АВЕКМНОРСТУХ]{2,3}\d{2,3}$"
    result = bool(re.match(pattern, cleaned))
    if not result:
        logger.warning(f"Не прошёл валидацию: original='{original}', cleaned='{cleaned}'")
        # Определяем недопустимые символы
        allowed = set("АВЕКМНОРСТУХ0123456789")
        invalid_chars = set(cleaned) - allowed
        if invalid_chars:
            logger.warning(f"Недопустимые символы: {invalid_chars}")
    return result

def send_email_via_exchange(car_number: str, point_key: str):
    point_addresses = {
        "mm6": "Миклухо-Маклая, д.6",
        "mm10k2": "Миклухо-Маклая, д.10к2",
        "ordzhonikidze": "Орджоникидзе, д.3",
    }
    address = point_addresses.get(point_key, "Неизвестная точка")
    credentials = Credentials(username=YOUR_EMAIL, password=YOUR_PASSWORD)
    try:
        account = Account(primary_smtp_address=YOUR_EMAIL, credentials=credentials, autodiscover=True, access_type='delegate')
    except Exception:
        config = Configuration(server='owa.ekdekb.ru', credentials=credentials)
        account = Account(primary_smtp_address=YOUR_EMAIL, config=config, autodiscover=False, access_type='delegate')
    
    # Формируем тело письма по вашему шаблону
    body = f"Прошу пропустить машину для разгрузки на {address}.\n{car_number}\nЗаранее спасибо.\n\n{SIGNATURE}"
    
    msg = Message(
        account=account,
        subject=f'Заявка на пропуск {car_number}',
        body=body,
        to_recipients=[Mailbox(email_address='bp@pfur.ru')]  # Поменяйте на bp@pfur.ru когда будете готовы
    )
    msg.send()
    logger.info(f"✅ Письмо отправлено для {car_number} (на {YOUR_EMAIL})")

def get_user_id_from_event(event):
    try:
        if hasattr(event, 'message') and hasattr(event.message, 'sender'):
            sender = event.message.sender
            return getattr(sender, 'user_id', None) or getattr(sender, 'id', None)
        if hasattr(event, 'user'):
            return getattr(event.user, 'user_id', None) or getattr(event.user, 'id', None)
        if hasattr(event, 'chat_id'):
            return event.chat_id
        return None
    except Exception as e:
        logger.error(f"Ошибка user_id: {e}")
        return None

bot = Bot(token=MAX_BOT_TOKEN)
dp = Dispatcher()
user_states = {}

@dp.bot_started()
async def bot_started(event: BotStarted):
    await event.bot.send_message(
        chat_id=event.chat_id,
        text="👋 Добро пожаловать в Бюро пропусков!\n\nНапишите /start чтобы начать оформление пропуска."
    )

@dp.message_created(Command('start'))
async def cmd_start(event: MessageCreated):
    user_id = get_user_id_from_event(event)
    if not user_id:
        return
    user_states.pop(user_id, None)

    await event.message.answer(
        "👋 Выберите точку разгрузки:\n\n"
        "Напишите цифру:\n"
        "1 — Миклухо-Маклая, д.6\n"
        "2 — Миклухо-Маклая, д.10к2\n"
        "3 — Орджоникидзе, д.3\n\n"
        "После этого введите номер автомобиля"
    )

@dp.message_created(F.message.body.text)
async def handle_plate_input(event: MessageCreated):
    user_id = get_user_id_from_event(event)
    if not user_id:
        return

    text = event.message.body.text.strip()
    logger.info(f"Получен текст: '{text}'")

    # === Обработка выбора точки (цифры 1,2,3) ===
    point_map = {
        "1": ("mm6", "Миклухо-Маклая, д.6(В точке Б въезд в подземную парковку на разгрузку)"),
        "2": ("mm10k2", "Миклухо-Маклая, д.10к2"),
        "3": ("ordzhonikidze", "Орджоникидзе, д.3"),
    }

    if text in point_map:
        point_key, point_name = point_map[text]
        user_states[user_id] = {"point_key": point_key, "point_name": point_name}
        await event.message.answer(f"✅ Вы выбрали: {point_name}\n\nТеперь введите номер автомобиля")
        return

    # === Обработка номера автомобиля ===
    state = user_states.get(user_id)
    if not state:
        await event.message.answer("❌ Сначала выберите точку разгрузки: /start")
        return

    if not is_valid_plate(text):
        await event.message.answer(
            "❌ Неверный формат номера.\n"
            "Допустимые буквы: А, В, Е, К, М, Н, О, Р, С, Т, У, Х\n"
            "Примеры: А123ВС777, К345ГВ786, В555ОР77\n"
            "Попробуйте ещё раз:"
        )
        return

    car_number = text.replace(" ", "").replace("-", "").upper()
    point_key = state["point_key"]
    point_name = state["point_name"]

    try:
        send_email_via_exchange(car_number, point_key)
    except Exception as e:
        logger.error(f"Ошибка email: {e}")
        await event.message.answer("⚠️ Ошибка отправки заявки. Попробуйте позже.")
        return

    # Отправляем схему проезда как ссылку (в MAX нет встроенной отправки фото через answer_photo)
    map_url = MAPS.get(point_key)
    if map_url:
        await event.message.answer(
            f"🗺️ Схема проезда: {point_name}\n{map_url}\n\n"
            f"🚛 Номер: {car_number}\n✅ Пропуск на 24 часа оформлен"
        )
    else:
        await event.message.answer(f"✅ Заявка для {car_number} принята!\nТочка: {point_name}")

    # Отправляем контакты (уже без дублирования)
    contacts = CONTACTS.get(point_key, "Контакты не найдены")
    await event.message.answer(contacts)

    user_states.pop(user_id, None)

async def main():
    logger.info("Запуск polling...")
    await bot.delete_webhook()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}")
        logger.critical(traceback.format_exc())