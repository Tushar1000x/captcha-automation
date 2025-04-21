from flask import Flask, render_template, request
import random, string
from PIL import Image, ImageDraw, ImageFont
import io
import base64

app = Flask(__name__)
current_captcha = ""
captcha_type = ""

def generate_text_captcha():
    text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    img = Image.new('RGB', (150, 60), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 40)
    draw.text((20, 10), text, font=font, fill=(0, 0, 0))
    return text, img

def generate_math_captcha():
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    op = random.choice(['+', '-'])
    question = f"{a} {op} {b}"
    result = str(eval(question))
    img = Image.new('RGB', (180, 60), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 35)
    draw.text((10, 10), f"Solve: {question}", font=font, fill=(0, 0, 0))
    return result, img

@app.route("/", methods=["GET", "POST"])
def login():
    global current_captcha, captcha_type

    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]
        cap = request.form["captcha"]

        if cap.strip().lower() == current_captcha.lower():
            return "✅ Logged in"
        else:
            return "❌ CAPTCHA incorrect"

    if random.choice([True, False]):
        captcha_type = "text"
        current_captcha, img = generate_text_captcha()
    else:
        captcha_type = "math"
        current_captcha, img = generate_math_captcha()

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_b64 = base64.b64encode(buffer.getvalue()).decode()

    return render_template("login.html", captcha_data=img_b64)

if __name__ == "__main__":
    app.run(debug=True)
