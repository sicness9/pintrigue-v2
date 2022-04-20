import io

from PIL import Image


def convert_image(image_old):
    size = 350, 350
    try:
        with Image.open(image_old) as im:
            output = io.BytesIO()
            im.thumbnail(size=size)
            im.save(output, format="WebP")
            output.seek(0)
            return output
    except Exception as e:
        return {"ERROR:", e}
