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

CAPTCHA_FILE_NAME = "captcha.png"

bot = telegram.Bot(TELEGRAM_BOT_TOKEN)

options = Options()
options.headless = False
driver = webdriver.Chrome("./chromedriver_linux64/chromedriver", options=options, service_log_path="chromedriver.log")

def wait_and_send_and_fill_captcha():
    captcha_img = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "img[src*='captcha']")))
    captcha_img.screenshot(CAPTCHA_FILE_NAME)
    bot.send_photo(photo=open(CAPTCHA_FILE_NAME, "rb"), chat_id=TELEGRAM_BOT_CHANNEL)
    captcha_input = driver.find_element_by_css_selector("input[title*='Codice']")
    captcha_input.send_keys(input("CAPTCHA: "))

# def fill_captcha(update, context):
#     user_input = update.to_dict()["channel_post"]["text"]
#     captcha_input = driver.find_element_by_css_selector("input[title*='Codice']")
#     captcha_input.send_keys(user_input)
#     os.kill(os.getpid(), signal.SIGINT)

# def message_listener():
#     """
#     Wait captchas responses from bot
#     """
#     updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
#     dispatcher = updater.dispatcher
#     dispatcher.add_handler(MessageHandler(Filters.text, fill_captcha))
#     updater.start_polling()
#     updater.idle()

if __name__ == "__main__":
    driver.get(f"https://prenotaonline.esteri.it/Login.aspx?ReturnUrl=%2Fdefault.aspx&cidsede={SEDE}")
    wait = WebDriverWait(driver, 10)

    #
    # Log-in
    #

    driver.find_element_by_name("BtnLogin").click()
    driver.find_element_by_name("UserName").send_keys(USUARIO)
    driver.find_element_by_name("Password").send_keys(PASSWORD)
    wait_and_send_and_fill_captcha()  # 1st captcha

    # message_listener()

    driver.find_element_by_css_selector("input[value='Login']").click()

    #
    # Formulario
    #

    time.sleep(1)  # wait below is not working
    solicite_un_turno = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_repFunzioni_ctl00_btnMenuItem")))
    solicite_un_turno.click()

    time.sleep(1)  # wait below is not working
    ciudadania = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_rpServizi_ctl02_btnNomeServizio")))
    ciudadania.click()

    driver.find_element_by_id("ctl00_ContentPlaceHolder1_acc_datiAddizionali1_mycontrol1").send_keys(DIRECCION)
    driver.find_element_by_id("ctl00_ContentPlaceHolder1_acc_datiAddizionali1_mycontrol2").send_keys(LOCALIDAD)
    driver.find_element_by_id("ctl00_ContentPlaceHolder1_acc_datiAddizionali1_mycontrol3").send_keys(CODIGO_POSTAL)
    driver.find_element_by_id("ctl00_ContentPlaceHolder1_acc_datiAddizionali1_btnContinua").click()

    #
    # Calendario
    #

    # driver.implicitly_wait(0)  # this is not working
    libre = None
    while libre is None:
        driver.refresh()
        libre = driver.find_element_by_css_selector(".calendarCellOpen input")
    libre.click()

    driver.find_element_by_id("ctl00_ContentPlaceHolder1_acc_Calendario1_repFasce_ctl01_btnConferma").click()

    wait_and_send_and_fill_captcha()  # 2nd captcha

    driver.find_element_by_id("ctl00_ContentPlaceHolder1_captchaConf").click()

    driver.save_screenshot('screenshot.png')
