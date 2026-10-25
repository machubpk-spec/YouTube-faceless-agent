from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def make_thumbnail(image_path, title_text, output_path="thumb.jpg"):
    img = Image.open(image_path).convert("RGBA").resize((1280, 720))
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([0, 460, 1280, 720], fill=(0, 0, 0, 180))
    img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_PATH, 54)
    except Exception:
        font = ImageFont.load_default()

    draw.text((40, 540), title_text.upper()[:38], font=font, fill="white")
    img.convert("RGB").save(output_path)
