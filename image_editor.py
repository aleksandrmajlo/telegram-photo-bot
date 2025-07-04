from PIL import Image, ImageDraw, ImageFont
import requests
import io

class ImageEditor:
    def __init__(self, font_url=None, font_size=32):
        self.font_url = font_url or "fonts/DejaVuSans.ttf"
        self.font_size = font_size

    def add_text(self, image_bytes, text, position=(10, 10), color=(255, 0, 0)):
        if not text or not isinstance(text, str):
           raise ValueError("Неверный или пустой текст для наложения")

        image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        txt_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        font = self.load_font()
        draw.text(position, text, font=font, fill=color + (255,))
        combined = Image.alpha_composite(image, txt_layer)

        output = io.BytesIO()
        combined.convert("RGB").save(output, format="JPEG")
        output.seek(0)
        return output


    def load_font(self):
        try:
            if self.font_url and self.font_url.startswith("http"):
                # Загружаем шрифт из интернета
                response = requests.get(self.font_url)
                response.raise_for_status()
                font_bytes = io.BytesIO(response.content)
                font = ImageFont.truetype(font_bytes, self.font_size)
            elif self.font_url:
                font = ImageFont.truetype(self.font_url, self.font_size)
            else:
                font = ImageFont.load_default()
        except Exception as e:
            print(f"[FONT LOAD ERROR]: {e}")
            font = ImageFont.load_default()
        return font    