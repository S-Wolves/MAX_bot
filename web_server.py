# web_server.py — ЕДИНЫЙ ФАЙЛ ДЛЯ RENDER
import os
import re
import logging
from aiohttp import web
from exchangelib import Account, Credentials, Message, Mailbox, Configuration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== НАСТРОЙКИ ==========
YOUR_EMAIL = "s.volkov@caterinburg.ru"
YOUR_PASSWORD = os.getenv("MAIL_PASSWORD", "")

SIGNATURE = """--
С уважением,
Сергей Волков
Управляющий
117198, г. Москва, ул. Миклухо-Маклая, 6, РУДН
т. сот.: +7 (961) 388-84-82
эл.почта: s.volkov@caterinburg.ru

www.caterinburg.ru
https://vk.com/caterinburg"""

def send_email(car_number: str, point_key: str):
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
    
    body = f"Прошу пропустить машину для разгрузки на {address}.\n{car_number}\nЗаранее спасибо.\n\n{SIGNATURE}"
    msg = Message(
        account=account,
        subject=f'Заявка на пропуск {car_number}',
        body=body,
        to_recipients=[Mailbox(email_address='bp@pfur.ru')]
    )
    msg.send()
    logger.info(f"Письмо отправлено для {car_number}")

# ========== HTML-страница (встроенная) ==========
HTML_PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Кейтеринбург — Пропуск</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 16px;
            background-color: #f5f5f5;
        }
        .container { max-width: 500px; margin: 0 auto; }
        h1 { font-size: 24px; margin-bottom: 8px; }
        .subtitle { color: #666; margin-bottom: 24px; font-size: 14px; }
        .points { display: flex; flex-direction: column; gap: 12px; margin-bottom: 24px; }
        .point-btn {
            background: white;
            border: 1px solid #ddd;
            border-radius: 12px;
            padding: 16px;
            text-align: left;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
        }
        .point-btn.selected { background: #007aff; border-color: #007aff; color: white; }
        .point-address { font-weight: 600; }
        .point-note { font-size: 12px; opacity: 0.7; margin-top: 4px; }
        .input-group { margin-bottom: 16px; }
        .input-group label { display: block; font-size: 14px; font-weight: 500; margin-bottom: 8px; }
        input {
            width: 100%;
            padding: 14px;
            border: 1px solid #ddd;
            border-radius: 12px;
            font-size: 16px;
            font-family: monospace;
            text-transform: uppercase;
        }
        input:focus { outline: none; border-color: #007aff; }
        button.submit {
            width: 100%;
            background: #007aff;
            color: white;
            border: none;
            border-radius: 12px;
            padding: 16px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 8px;
        }
        button.submit:disabled { background: #ccc; }
        .status {
            margin-top: 16px;
            padding: 12px;
            border-radius: 12px;
            font-size: 14px;
            text-align: center;
        }
        .status.success { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
        .status.loading { background: #e2f0ff; color: #004085; }
        hr { margin: 20px 0; border: none; border-top: 1px solid #ddd; }
        .footer { font-size: 12px; color: #999; text-align: center; margin-top: 24px; }
    </style>
</head>
<body>
<div class="container">
    <h1>🚚 Кейтеринбург</h1>
    <div class="subtitle">Оформление пропуска для въезда</div>
    <div class="points">
        <button class="point-btn" data-point="mm6" data-name="Миклухо-Маклая, д.6">
            <div class="point-address">📍 Миклухо-Маклая, д.6</div>
            <div class="point-note">Въезд в подземную парковку</div>
        </button>
        <button class="point-btn" data-point="mm10k2" data-name="Миклухо-Маклая, д.10к2">
            <div class="point-address">📍 Миклухо-Маклая, д.10к2</div>
        </button>
        <button class="point-btn" data-point="ordzhonikidze" data-name="Орджоникидзе, д.3">
            <div class="point-address">📍 Орджоникидзе, д.3</div>
        </button>
    </div>
    <div class="input-group">
        <label>🚛 Номер автомобиля</label>
        <input type="text" id="plate" placeholder="Например: А123ВС777" maxlength="12" autocomplete="off">
    </div>
    <button class="submit" id="submitBtn">Оформить пропуск</button>
    <div id="status" class="status" style="display: none;"></div>
    <hr>
    <div class="footer">Пропуск действует 24 часа<br>После оформления схема проезда и контакты придут в чат</div>
</div>
<script>
    const pointBtns = document.querySelectorAll('.point-btn');
    const plateInput = document.getElementById('plate');
    const submitBtn = document.getElementById('submitBtn');
    const statusDiv = document.getElementById('status');
    let selectedPoint = null;
    let selectedPointName = null;

    plateInput.addEventListener('input', function(e) { this.value = this.value.toUpperCase(); });
    pointBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            pointBtns.forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            selectedPoint = btn.dataset.point;
            selectedPointName = btn.dataset.name;
        });
    });
    submitBtn.addEventListener('click', async () => {
        const plate = plateInput.value.trim().replace(/\\s+/g, '').replace(/-/g, '');
        if (!selectedPoint) { showStatus('Выберите точку разгрузки', 'error'); return; }
        if (!plate) { showStatus('Введите номер автомобиля', 'error'); return; }
        const plateRegex = /^[АВЕКМНОРСТУХ]\\d{3}[АВЕКМНОРСТУХ]{2,3}\\d{2,3}$/i;
        if (!plateRegex.test(plate)) { showStatus('Неверный формат номера. Пример: А123ВС777', 'error'); return; }
        submitBtn.disabled = true;
        showStatus('Отправка...', 'loading');
        try {
            const response = await fetch('/api/request-pass', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ point_key: selectedPoint, car_number: plate })
            });
            const result = await response.json();
            if (response.ok) {
                showStatus('✅ Заявка отправлена! Пропуск на 24 часа.', 'success');
                pointBtns.forEach(b => b.classList.remove('selected'));
                selectedPoint = null;
            } else {
                showStatus(result.error || 'Ошибка', 'error');
            }
        } catch (err) {
            showStatus('Ошибка соединения', 'error');
        } finally {
            submitBtn.disabled = false;
        }
    });
    function showStatus(message, type) {
        statusDiv.textContent = message;
        statusDiv.className = `status ${type}`;
        statusDiv.style.display = 'block';
        setTimeout(() => { if (statusDiv.className === `status ${type}`) statusDiv.style.display = 'none'; }, 3000);
    }
</script>
</body>
</html>"""

# ========== ОБРАБОТЧИКИ ВЕБ-СЕРВЕРА ==========
async def handle_index(request):
    return web.Response(text=HTML_PAGE, content_type='text/html')

async def handle_request_pass(request):
    try:
        data = await request.json()
        car_number = data.get('car_number', '').upper()
        point_key = data.get('point_key')
        if not car_number or not point_key:
            return web.json_response({'error': 'Не все данные'}, status=400)
        pattern = r"^[АВЕКМНОРСТУХ]\d{3}[АВЕКМНОРСТУХ]{2,3}\d{2,3}$"
        if not re.match(pattern, car_number):
            return web.json_response({'error': 'Неверный формат номера'}, status=400)
        send_email(car_number, point_key)
        return web.json_response({'status': 'ok'})
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return web.json_response({'error': str(e)}, status=500)

app = web.Application()
app.router.add_get('/', handle_index)
app.router.add_post('/api/request-pass', handle_request_pass)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Запуск на порту {port}")
    web.run_app(app, host='0.0.0.0', port=port)
