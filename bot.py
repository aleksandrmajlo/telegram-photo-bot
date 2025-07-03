from flask import Flask, request
import telegram
import logging
import asyncio
from PIL import Image, ImageDraw, ImageFont
import os

TOKEN = "7811367207:AAH39vjyrr3mqz1dvBmgr25WBf9GpGat8LI"
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/webhook', methods=['POST'])
def webhook():
    # Создаём loop (и НЕ закрываем!)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        data = request.get_json(force=True)
        logging.info(f"Получен update: {data}")
        update = telegram.Update.de_json(data, bot)

        if update.message:
            chat_id = update.message.chat.id

            # Фото
            if update.message.photo:
                file_id = update.message.photo[-1].file_id
                file = loop.run_until_complete(bot.get_file(file_id))

                input_path = f"input_{chat_id}.jpg"
                output_path = f"output_{chat_id}.jpg"

                # Скачивание файла
                loop.run_until_complete(file.download_to_drive(input_path))

                # Обработка изображения
                image = Image.open(input_path).convert("RGB")
                draw = ImageDraw.Draw(image)

                try:
                    font = ImageFont.truetype("arial.ttf", 36)
                except:
                    font = ImageFont.load_default()

                
                if update.message.caption:
                    text = update.message.caption
                else:
                    text = "hello"

                # Новый способ — textbbox (вместо textsize)
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = image.width - text_width - 20
                y = image.height - text_height - 20

                draw.text((x, y), text, font=font, fill=(255, 255, 255))
                image.save(output_path)

                # Отправка фото назад
                with open(output_path, "rb") as photo:
                    loop.run_until_complete(bot.send_photo(chat_id=chat_id, photo=photo))

                os.remove(input_path)
                os.remove(output_path)

            else:
                # Обычное текстовое сообщение
                message = update.message.text
                loop.run_until_complete(bot.send_message(chat_id=chat_id, text=f"Вы написали: {message}"))

        else:
            logging.info("Update не содержит message.")

    except Exception as e:
        logging.error(f"Ошибка обработки webhook: {e}")

    return 'ok', 200


@app.route('/')
def index():
    return 'Бот работает!'

# if __name__ == '__main__':
    # app.run(port=8080, threaded=True)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, threaded=True)    