import os
import signal
import time

import telegram
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from telegram.ext import Filters, MessageHandler, Updater

load_dotenv()

SEDE = os.getenv("SEDE")
USUARIO = os.getenv("USUARIO")
PASSWORD = os.getenv("PASSWORD")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_BOT_CHANNEL = os.getenv("TELEGRAM_BOT_CHANNEL")
DIRECCION = os.getenv("DIRECCION")
LOCALIDAD = os.getenv("LOCALIDAD")
CODIGO_POSTAL = os.getenv("CODIGO_POSTAL")

SHORT_LOGIN_CAPTCHA_IMG = "captcha_1.png"
LONG_CONFIRMATION_CAPTCHA_IMG = "captcha_2.png"

bot = telegram.Bot(TELEGRAM_BOT_TOKEN)

options = Options()
options.headless = True
driver = webdriver.Chrome("./chromedriver_linux64/chromedriver", options=options)

def fill_captcha(update, context):
    user_input = update.to_dict()["channel_post"]["text"]
    captcha_input = driver.find_element_by_id("loginCaptcha")
    captcha_input.send_keys(user_input)
    os.kill(os.getpid(), signal.SIGINT)

def message_listener():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text, fill_captcha))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    driver.get(f"https://prenotaonline.esteri.it/Login.aspx?ReturnUrl=%2Fdefault.aspx&cidsede={SEDE}")
    wait = WebDriverWait(driver, 10)

    #
    # Log-in
    #

    driver.find_element_by_name("BtnLogin").click()
    bot.send_message(text="Logging", chat_id=TELEGRAM_BOT_CHANNEL)
    driver.find_element_by_name("UserName").send_keys(USUARIO)
    driver.find_element_by_name("Password").send_keys(PASSWORD)

    try:
        captcha_img = wait.until(
            EC.visibility_of_element_located((By.ID, "captchaLogin"))
        )
    except:
        print("No carga captcha")

    captcha_img.screenshot(SHORT_LOGIN_CAPTCHA_IMG)
    bot.send_photo(photo=open(SHORT_LOGIN_CAPTCHA_IMG, "rb"), chat_id=TELEGRAM_BOT_CHANNEL)

    message_listener()

    driver.find_element_by_id("BtnConfermaL").click()

    #
    # Turno
    #

    # driver.find_element_by_id("ctl00_repFunzioni_ctl00_btnMenuItem").click()
    # driver.find_element_by_id("ctl00_ContentPlaceHolder1_rpServizi_ctl02_btnNomeServizio").click()

    # driver.find_element_by_id("ctl00_ContentPlaceHolder1_acc_datiAddizionali1_mycontrol1").send_keys(DIRECCION)
    # driver.find_element_by_id("ctl00_ContentPlaceHolder1_acc_datiAddizionali1_mycontrol2").send_keys(LOCALIDAD)
    # driver.find_element_by_id("ctl00_ContentPlaceHolder1_acc_datiAddizionali1_mycontrol3").send_keys(CODIGO_POSTAL)
    # driver.find_element_by_id("ctl00_ContentPlaceHolder1_acc_datiAddizionali1_btnContinua").click()

