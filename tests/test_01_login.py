from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

def test_login_valid():
    driver_path = os.path.join(os.path.dirname(__file__), '..', 'chromedriver.exe')
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)
    driver.get("http://158.160.87.146:5000/login")

    wait = WebDriverWait(driver, 10)
    username_input = wait.until(EC.presence_of_element_located((By.NAME, "login")))
    password_input = driver.find_element(By.NAME, "password")
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")

    username_input.send_keys("admin")
    password_input.send_keys("admin")
    submit_button.click()

    wait.until(lambda d:  "Список пользователей" in d.page_source)

    # Получаем токен из localStorage по ключу 'token'
    token = driver.execute_script("return window.localStorage.getItem('token');")
    
    # Сохраняем токен в файл
    with open("auth_token.txt", "w") as f:
        f.write(token if token else "")

    driver.quit()
