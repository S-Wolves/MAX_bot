import asyncio
import logging
import os
from aiohttp import web
from maxapi import Bot, Dispatcher, F
from maxapi.types import BotStarted, MessageCreated

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен основного бота из переменной окружения
MAX_BOT_TOKEN = os.getenv("BOT_TOKEN")
if not MAX_BOT_TOKEN:
    logger.error("BOT_TOKEN не задан в переменных окружения")
    exit(1)

bot = Bot(token=MAX_BOT_TOKEN)
dp = Dispatcher()
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

# --- Обработчики команд бота ---
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
    
    if text == '/start':
        greeted_users.add(user_id)
        await event.message.answer(
            "🚚 **Кейтеринбург**\n\n"
            "Добро пожаловать! Я помогу вам оформить пропуск для въезда.\n\n"
            "👇 **Нажмите на кнопку слева от строки ввода**, чтобы открыть форму заказа пропуска.\n\n"
            "После заполнения вы получите схему проезда и контакты склада."
        )
        return
    
    if user_id in greeted_users:
        await event.message.answer(
            "👇 **Нажмите на кнопку слева от строки ввода**, чтобы открыть форму заказа пропуска."
        )
    else:
        greeted_users.add(user_id)
        await event.message.answer(
            "🚚 **Кейтеринбург**\n\n"
            "Добро пожаловать! Я помогу вам оформить пропуск для въезда.\n\n"
            "👇 **Нажмите на кнопку слева от строки ввода**, чтобы открыть форму заказа пропуска.\n\n"
            "После заполнения вы получите схему проезда и контакты склада."
        )

# --- Минимальный веб-сервер для Render ---
async def health_check(request):
    return web.Response(text="OK")

async def run_web():
    app = web.Application()
    # Добавляем обработчик для корневого пути
    async def handle_root(request):
        return web.Response(text="OK")
    app.router.add_get('/', handle_root)
    app.router.add_get('/health', lambda req: web.Response(text="OK"))
    
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Health-check сервер запущен на порту {port}")
    while True:
        await asyncio.sleep(3600)

async def main():
    logger.info("Запуск greeting бота...")
    await bot.delete_webhook()
    # Запускаем веб-сервер в фоне
    asyncio.create_task(run_web())
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
