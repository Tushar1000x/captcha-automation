from flask import Flask, render_template, request
from captcha.image import ImageCaptcha
from PIL import Image
import pytesseract
import base64
import io
import random
import string

app = Flask(__name__)

# Store current answer globally
current_captcha_answer = ""

# Set tesseract path for Windows users
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Generate a random text CAPTCHA
def generate_text_captcha():
    global current_captcha_answer
    text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    current_captcha_answer = text

    image_gen = ImageCaptcha(width=160, height=60)
    image = image_gen.generate_image(text)
    return image

# Convert image to base64 string for embedding
def image_to_base64(img):
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

@app.route("/", methods=["GET", "POST"])
def login():
    global current_captcha_answer

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_input = request.form["captcha"].strip().upper()

        if user_input == current_captcha_answer:
            return "✅ Logged in"
        else:
            return "❌ CAPTCHA incorrect"

    captcha_img = generate_text_captcha()  # Only text CAPTCHA now
    captcha_data = image_to_base64(captcha_img)
    return render_template("login.html", captcha_data=captcha_data)

if __name__ == "__main__":
    app.run(debug=True)
