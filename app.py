from pyzbar.pyzbar import decode
from flask import Flask, request, render_template
import izly_api
import base64
from PIL import Image
import io
import re
import qrcode

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )

        # Get the username and password from the form
        username = request.form['username']
        password = request.form['password']

        # Generate the QR code from Izly
        credentials = izly_api.get_credentials(*izly_api.get_csrf(), username, password)
        base64_qrcodes = izly_api.get_qrcode(credentials)[0]
        base64_image = str(re.search(r"base64,(.*)", base64_qrcodes["Src"]).group(1))
        img_bytes = base64.b64decode(base64_image)

        # Decode the QR code
        image = Image.open(io.BytesIO(img_bytes))
        decoded_data = decode(image)[0].data.decode("utf-8")

        # Add data to the QR code instance
        qr.add_data(decoded_data)
        qr.make(fit=True)

        # Generate the QR code image
        img = qr.make_image(fill_color="black", back_color="white")

        byte_buffer = io.BytesIO()
        img.save(byte_buffer, format="PNG")
        qr_code_bytes = byte_buffer.getvalue()

        # Return the QR code as an image
        return qr_code_bytes, 200, {'Content-Type': 'image/png'}
    else:
        # If the request is a GET request, return the HTML form
        return render_template('index.html')


if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
