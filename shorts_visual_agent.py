from PIL import Image, ImageFilter

CANVAS_W, CANVAS_H = 1080, 1920

def reframe_to_vertical(image_path, output_path):
    img = Image.open(image_path).convert("RGB")
    bg = img.resize((CANVAS_W, CANVAS_H)).filter(ImageFilter.GaussianBlur(25))
    bg = bg.point(lambda p: int(p * 0.45))

    scale = CANVAS_W / img.width
    fg_h = min(int(img.height * scale), CANVAS_H)
    fg = img.resize((CANVAS_W, fg_h))

    canvas = bg.copy()
    canvas.paste(fg, (0, (CANVAS_H - fg_h) // 2))
    canvas.save(output_path)
    return output_path
