from flask import Flask, request
import telegram
import logging
import asyncio
from PIL import Image, ImageDraw, ImageFont
import os
import sqlite3
from datetime import datetime
import subprocess
from image_editor import ImageEditor

TOKEN = "7811367207:AAH39vjyrr3mqz1dvBmgr25WBf9GpGat8LI"
bot = telegram.Bot(token=TOKEN)

# Подключение к базе данных
conn = sqlite3.connect('messages.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        message_text TEXT,
        received_at TEXT
    )
''')
conn.commit()


app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


@app.route('/')
def index():
    return 'Бот работает!'

@app.route('/admin')
def admin():
    cursor.execute('SELECT chat_id, message_text, received_at FROM messages ORDER BY id DESC LIMIT 100')
    rows = cursor.fetchall()
    html = """
    <html>
    <head>
        <title>Админка сообщений</title>
        <style>
            body { font-family: sans-serif; padding: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { padding: 8px 12px; border: 1px solid #ccc; }
            th { background-color: #f5f5f5; }
        </style>
    </head>
    <body>
        <h2>Последние 100 сообщений</h2>
        <table>
            <tr>
                <th>Chat ID</th>
                <th>Сообщение</th>
                <th>Время</th>
            </tr>
    """

    for row in rows:
        chat_id, text, timestamp = row
        html += f"<tr><td>{chat_id}</td><td>{text}</td><td>{timestamp}</td></tr>"

    html += "</table></body></html>"

    return html

@app.route('/clear')
def clear():
    cursor.execute('DELETE FROM messages')
    conn.commit()
    return 'Сообщения очищены!'


    port = 8082  # или другой свободный порт
    adminer_path = os.path.join(os.getcwd(), 'adminer', 'adminer.php')

    # Проверяем, уже ли Adminer не запущен
    try:
        subprocess.check_output(['lsof', f'-i:{port}'])
        return f'<p>Adminer уже запущен на <a href="http://localhost:{port}">http://localhost:{port}</a></p>'
    except subprocess.CalledProcessError:
        # Не запущен — запускаем
        subprocess.Popen(['php', '-S', f'localhost:{port}', adminer_path])
        return f'<p>Adminer запущен на <a href="http://localhost:{port}">http://localhost:{port}</a></p>'    

@app.route('/webhook', methods=['POST'])
def webhook():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        data = request.get_json(force=True)
        logging.info(f"Получен update: {data}")
        update = telegram.Update.de_json(data, bot)

        if update.message:
            chat_id = update.message.chat.id

            # === Фото ===
            if update.message.photo:
                file_id = update.message.photo[-1].file_id
                file = loop.run_until_complete(bot.get_file(file_id))

                input_path = f"input_{chat_id}.jpg"
                output_path = f"output_{chat_id}.jpg"

                # Скачивание фото
                loop.run_until_complete(file.download_to_drive(input_path))

                # Получаем текст (caption или fallback)
                text = update.message.caption or "hello"

                # Сохраняем caption в SQLite
                cursor.execute(
                    'INSERT INTO messages (chat_id, message_text, received_at) VALUES (?, ?, ?)',
                    (chat_id, text, datetime.utcnow().isoformat())
                )
                conn.commit()

                # === Используем ImageEditor ===
                from image_editor import ImageEditor
                editor = ImageEditor(font_size=36)
                with open(input_path, 'rb') as img_file:
                    result = editor.add_text(img_file.read(), text)

                with open(output_path, "wb") as f:
                    f.write(result.read())

                # Отправляем обратно
                with open(output_path, "rb") as photo:
                    loop.run_until_complete(bot.send_photo(chat_id=chat_id, photo=photo))

                # Удаляем временные файлы
                os.remove(input_path)
                os.remove(output_path)

            else:
                # === Текстовое сообщение ===
                message = update.message.text
                cursor.execute(
                    'INSERT INTO messages (chat_id, message_text, received_at) VALUES (?, ?, ?)',
                    (chat_id, message, datetime.utcnow().isoformat())
                )
                conn.commit()

                loop.run_until_complete(bot.send_message(chat_id=chat_id, text=f"Вы написали: {message}"))

        else:
            logging.info("Update не содержит message.")

    except Exception as e:
        logging.error(f"Ошибка обработки webhook: {e}")

    return 'ok', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, threaded=True)    