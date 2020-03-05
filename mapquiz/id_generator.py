import secrets
from pathlib import Path

import qrcode
from PIL import Image
from django.template.defaultfilters import slugify

logo_path = Path(__file__).parent.absolute()  # Absolute path of this directory
logo_path = str(logo_path.joinpath("rural.png"))


def generate_uri_code(max_length):
    target_length = max(4, max_length - 4)
    # Approximately 1.3 characters per byte, see https://docs.python.org/3/library/secrets.html
    nbytes = int(target_length / 1.3)
    token = secrets.token_urlsafe(nbytes)
    return slugify(token)


def generate_qrcode(string):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q)
    qr.add_data(string)
    qr.make()
    img = qr.make_image()
    img = img.convert("RGB")

    logo = Image.open(logo_path)
    img.paste(logo, (img.size[0] // 2 - logo.size[0] // 2, img.size[1] // 2 - logo.size[1] // 2), logo)
    return img
