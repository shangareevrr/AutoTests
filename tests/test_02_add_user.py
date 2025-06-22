import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

# Получаем токен из файла и открываем браузер с localStorage
def create_driver_with_token():
# Путь к chromedriver
    driver_path = os.path.join(os.path.dirname(__file__), '..', 'chromedriver.exe')
    service = Service(driver_path)

    # Настройки для headless режима
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # Новый headless режим (начиная с Chrome 109+)
    options.add_argument("--disable-gpu")   # Отключает GPU (по умолчанию в headless)
    options.add_argument("--no-sandbox")    # Часто требуется в CI/серверных окружениях
    options.add_argument("--window-size=1920,1080")  # Размер окна, полезен для рендеринга

    # Запускаем браузер
    driver = webdriver.Chrome(service=service, options=options)

    # Открываем главную страницу
    driver.get("http://158.160.87.146:5000")

    # Подгружаем токен из файла и вставляем его в localStorage
    with open("auth_token.txt", "r") as f:
        token = f.read().strip()
    driver.execute_script(f"window.localStorage.setItem('token', '{token}')")

    # Обновляем страницу, чтобы применился токен
    driver.refresh()

    return driver


# Функция заполняет форму
def fill_form(driver, name="", age="", gender="", date="", is_active=True):
    driver.get("http://158.160.87.146:5000/add-user")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "name")))

    driver.find_element(By.ID, "name").send_keys(name)
    driver.find_element(By.ID, "age").send_keys(str(age))
    driver.find_element(By.ID, "gender").send_keys(gender)
    driver.find_element(By.ID, "date_birthday").send_keys(date)

    checkbox = driver.find_element(By.ID, "isActive")
    if checkbox.is_selected() != is_active:
        checkbox.click()

    driver.find_element(By.ID, "add-btn").click()

# читаем блок messageContainer
def get_message(driver):
    return WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "messageContainer"))
    ).text
#читаем блоки Error
def wait_for_error(driver, element_id, timeout=5):
    """Ожидает, пока элемент ошибки станет видимым"""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.ID, element_id))
    )

#  Тест 1: Успешное добавление пользователя
def test_add_user_valid_all_fields():
# Создаём WebDriver с уже установленным токеном и переходом на /add-user
    driver = create_driver_with_token()
    try:
        # Заполняем форму: имя, возраст, пол, дата рождения (в формате YYYY-MM-DD), активность
        fill_form(driver, "Иван", 25, "М", "01-01-1994", True)

        # Ждём, пока появится сообщение об успешном добавлении
        wait = WebDriverWait(driver, 10)
        wait.until(
            EC.text_to_be_present_in_element((By.ID, "messageContainer"), "Пользователь успешно добавлен")
        )

        # Извлекаем текст сообщения и проверяем его
        message = driver.find_element(By.ID, "messageContainer").text
        assert "Пользователь успешно добавлен" in message

    finally:
        # Закрываем браузер даже при ошибке
        driver.quit()

# Тест 2: Пропущено имя
def test_add_user_missing_name():
    driver = create_driver_with_token()
    try:
        fill_form(driver, "", 19, "М", "1994-01-01", True)

        # Ожидание появления сообщения ошибки
        message = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "nameError"))
        )
        assert "Поле обязательно" in message.text
    finally:
        driver.quit()

#Тест 3: Пропущен возраст
def test_add_user_missing_age():
    driver = create_driver_with_token()
    try:
        fill_form(driver, "Катя", "", "Ж", "1996-01-01", False)

        # Ожидаем отображение ошибки для поля возраста
        error = wait_for_error(driver, "ageError")
        message = error.text

        assert "Поле обязательно" in message
    finally:
        driver.quit()

#Тест 4: Проверка на отрицательный возраст
def test_add_user_invalid_age_low():
    driver = create_driver_with_token()
    try:
        fill_form(driver, "Шерлок", -10, "М", "1900-01-01", True)
        container_text = driver.find_element(By.ID, "messageContainer").text
        assert "ошибка" in container_text.lower()
    finally:
        driver.quit()

#Тест 5: Проверка на длину поля возраст
def test_add_user_invalid_age_high():
    driver = create_driver_with_token()
    try:
        fill_form(driver, "Ктулху", 10000, "М", "1000-12-12", False)
        container_text = driver.find_element(By.ID, "messageContainer").text
        assert "ошибка" in container_text.lower()
    finally:
        driver.quit()

#Тест 6: Проверка поля пол на соотвествие ТЗ "М" или "Ж"
def test_add_user_invalid_gender():
    driver = create_driver_with_token()
    try:
        fill_form(driver, "Джон", 30, "мужчина", "1990-05-05", True)
        container_text = driver.find_element(By.ID, "messageContainer").text
        assert "ошибка" in container_text.lower()
    finally:
        driver.quit()
