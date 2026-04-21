import asyncio
import logging
from maxapi import Bot, Dispatcher, F
from maxapi.types import BotStarted, MessageCreated

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен вашего тестового бота
import os
MAX_BOT_TOKEN = os.getenv("BOT_TOKEN", "токен_по_умолчанию")

bot = Bot(token=MAX_BOT_TOKEN)
dp = Dispatcher()

# Хранилище для отслеживания, кому уже отправили приветствие
greeted_users = set()

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

@dp.bot_started()
async def bot_started(event: BotStarted):
    user_id = event.chat_id
    greeted_users.add(user_id)
    await event.bot.send_message(
        chat_id=event.chat_id,
        text="🚚 **Кейтеринбург**\n\n"
             "Добро пожаловать! Я помогу вам оформить пропуск для въезда.\n\n"
             "👇 **Нажмите на кнопку слева от строки ввода**, чтобы открыть форму заказа пропуска.\n\n"
             "После заполнения вы получите схему проезда и контакты склада."
    )

@dp.message_created(F.message.body.text)
async def handle_message(event: MessageCreated):
    user_id = get_user_id_from_event(event)
    if not user_id:
        return
    
    text = event.message.body.text.strip()
    logger.info(f"Получен текст: '{text}'")
    
    # Если пользователь написал /start, отправляем полное приветствие
    if text == '/start':
        greeted_users.add(user_id)
        await event.message.answer(
            "🚚 **Кейтеринбург**\n\n"
            "Добро пожаловать! Я помогу вам оформить пропуск для въезда.\n\n"
            "👇 **Нажмите на кнопку слева от строки ввода**, чтобы открыть форму заказа пропуска.\n\n"
            "После заполнения вы получите схему проезда и контакты склада."
        )
        return
    
    # Если пользователь уже получал приветствие, отвечаем коротко
    if user_id in greeted_users:
        await event.message.answer(
            "👇 **Нажмите на кнопку слева от строки ввода**, чтобы открыть форму заказа пропуска."
        )
    else:
        # Первое сообщение от пользователя (не /start) — отправляем полное приветствие
        greeted_users.add(user_id)
        await event.message.answer(
            "🚚 **Кейтеринбург**\n\n"
            "Добро пожаловать! Я помогу вам оформить пропуск для въезда.\n\n"
            "👇 **Нажмите на кнопку слева от строки ввода**, чтобы открыть форму заказа пропуска.\n\n"
            "После заполнения вы получите схему проезда и контакты склада."
        )

async def main():
    logger.info("Запуск greeting бота...")
    await bot.delete_webhook()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
