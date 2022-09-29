import logging
import time
import datetime
import os
import json
from pathlib import Path
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

LOGIN = '+79270306870'
PASSWORD = 'K.njdf09'


class Parser:
    """Открывает браузер (хром) заходит на сайт, проверяет наличие решеных обращений,
    сравнивает с БД, скачивает файлы"""
    URL = 'https://www.gosuslugi.ru/'
    search_for_days_before = 7

    def __init__(self, login, password, timeaut=7):
        self.login = login
        self.password = password
        self.timeaut = timeaut
        try:
            option = ChromeOptions()
            # option.add_argument('dom.webdriver.enabled', False)
            # option.add_argument("--disable-blink-features=AutomationControlled")
            option.add_argument('--log-level=5')
            option.add_argument("--start-maximized")
            option.headless = False
            self.driver = Chrome(service=Service(ChromeDriverManager().install()), options=option)
            # self.driver.set_window_size(1920, 1080)
            logging.info(f'Браузер открыт')
        except:
            logging.error('Веб драйвер не работает!!!')
            raise Exception('Веб драйвер не работает!!!')
        try:
            self.driver.get(self.URL)
            logging.info(f'Открываю Госуслуги')
            time.sleep(self.timeaut)
        except:
            logging.error('Не удалось открыть ДЭБ!!!')
            raise Exception('Не удалось открыть ДЭБ!!!')

    def __del__(self):
        self.driver.close()
        self.driver.quit()
        logging.info(f'Браузер закрыт')

    def authorization_user(self):
        try:
            self.driver.find_element(By.XPATH, '//button/span[contains(text(), "Войти")]').click()
            time.sleep(self.timeaut)
        except:
            logging.error('Ошибка парсинга!!! Не найдена кнопка входа')
            raise Exception()
        try:
            input_login = self.driver.find_element(By.XPATH, '//input[@id="login"]')
            input_login.click()
            input_login.clear()
            input_login.send_keys(self.login)
            input_password = self.driver.find_element(By.XPATH, '//input[@id="password"]')
            input_password.click()
            input_password.clear()
            input_password.send_keys(self.password)
            self.driver.find_element(By.XPATH, '//button[contains(text(), "Войти")]').click()
        except:
            logging.error('Ошибка парсинга!!! При вводе данных авторизации')
            raise Exception()
        logging.info(f'Авторизация прошла успешно')

    def page_scrolling(self):
        self.driver.find_element(By.TAG_NAME, 'html').send_keys(Keys.END)
        logging.info(f'Прокручиваю страницу')

    def search_statements(self):
        while True:
            try:
                statements_driver = self.driver.find_elements(By.XPATH, '//a[contains(@href,"/order/")]')
                date_messages_final = statements_driver[-1].find_element(By.XPATH, './div/div/div[1]/div/div[2]/div').text
            except:
                logging.error('Ошибка парсинга!!! Не удалось найти заявки')
                raise Exception()
            control_date = datetime.datetime.now().date() - datetime.timedelta(days=self.search_for_days_before)
            date_messages_final = datetime.datetime.strptime(date_messages_final, '%d.%m.%y в %H:%M').date()
            logging.info(f'Заявки найдены. Дата последнего сообщения на странице: {date_messages_final}')
            if date_messages_final > control_date:
                self.page_scrolling()
            else:
                break
        return statements_driver

    def get_statements(self):
        self.statements = []
        self.driver.find_element(By.XPATH, '//a/span[contains(text(), "Заявления")]').click()
        time.sleep(self.timeaut)
        statements_driver = self.search_statements()
        try:
            for elm in statements_driver:
                link = elm.get_attribute('href')
                status = elm.find_element(By.XPATH, './/div[@class="visually-hidden"]').text
                number = elm.find_element(By.XPATH, './div/div/div[1]/div/div[1]').text
                date_messages = elm.find_element(By.XPATH, './div/div/div[1]/div/div[2]').text
                name = elm.find_element(By.XPATH, './/h4').text
                self.statements.append({
                    'link': link,
                    'status': status,
                    'number': number,
                    'date_messages': date_messages,
                    'name': name
                })
        except:
            logging.error('Ошибка парсинга!!! Не удалось найти заявки')
            raise Exception()
        logging.info(f'Информация о всех видимых заявках собрана')
        return self.statements

    def get_date_acceptane_in_deb(self, name_doc):
        try:
            input_poisk = self.driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Поиск"]')
            input_poisk.click()
            input_poisk.clear()
            input_poisk.send_keys(name_doc)
            button_poisk = self.driver.find_element(By.CSS_SELECTOR, 'button[id="searchButton"]')
            button_poisk.click()
            time.sleep(self.timeaut)
            try:
                self.tr_doc = self.driver.find_element(By.XPATH, f"//td[contains(text(), '{name_doc}')]")
            except:
                self.tr_doc = None
                logging.error('Документ в ДЭБ не найден!!!')
                raise Exception('Документ в ДЭБ не найден!!!')
            logging.info(f'Найден документ: {self.tr_doc.text}')
            data_acceptance = self.tr_doc.find_element(By.XPATH, "following::td[1]").text
            logging.info(f'Дата утверждения: {data_acceptance}')
        except:
            logging.error('Ошибка!!! Ошибка парсинга при поиске документа')
            raise Exception()
        return data_acceptance

    def downloads_doc_from_deb(self, name_doc):
        if self.tr_doc == None:
            self.get_date_acceptane_in_deb(name_doc)
        try:
            self.tr_doc.click()
            time.sleep(self.timeaut)
            tr_file = self.tr_doc.find_element(By.XPATH, "parent::*/following::td[1]")
            icons = tr_file.find_elements(By.XPATH, "//i[contains(concat(' ', @class, ' '), 'mdi-file-word')]")
            for icon in icons:
                a_file = icon.find_element(By.XPATH, "parent::*/parent::*//a")
                name_file = a_file.text
                if 'уф' in name_file.casefold() or 'изм' in name_file.casefold():
                    continue
                else:
                    word_doc = a_file
                    break
            try:
                word_doc.click()
            except:
                logging.error('Документ в word не найден!')
                raise Exception()
            logging.info(f'Скачиваю файл: {name_file}')
            time.sleep(self.timeaut)
        except:
            logging.error('Ошибка!!! Ошибка парсинга при скачивании документа')
            raise Exception()
        try:
            path_file = self._get_path_duwnload_file(name_file)
        except:
            logging.info(f'Жду еще 15 секунд.')
            time.sleep(15)
            path_file = self._get_path_duwnload_file(name_file)
        return path_file

    # Получить путь к скаченому файлу
    def get_path_duwnload_file(self, name_file: str):
        try:
            downloads_path = str(Path.home() / "Downloads")
            result = []
            for root, dirs, files in os.walk(downloads_path):
                for f in files:
                    if name_file in f:
                        path_file = os.path.join(root, f)
                        time_save = os.path.getmtime(path_file)
                        result.append((time_save, path_file))
            result.sort(reverse=True)
            path_file = result[0][1]
            logging.info(f'Путь к скаченомц файлу: {path_file}')
            return path_file
        except:
            logging.error(f'Ошибка!!! Не удалось скачать файл')
            raise Exception()


def create_dir(name_dir: str):
    if not os.path.exists(name_dir):
        os.mkdir(name_dir)
        return True


def save_file():
    pass


def chek_application_number(application_number: str):
    pass


def timer(hour, functin):
    while True:
        # Тайм зона Москва +3
        time_zone = datetime.timezone(datetime.timedelta(hours=3))
        current_time = datetime.datetime.now(time_zone).time()
        if datetime.time(hour) < current_time:
            functin()
            time_sleep = (24 - current_time.hour) * 3600
            time.sleep(time_sleep)
        else:
            time.sleep(60)


def test():
    print(datetime.datetime.now().time())


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    create_dir(name_dir='.\Госуслуги')
    # timer(1, test)
    parser = Parser(login=LOGIN, password=PASSWORD)
    parser.authorization_user()
    time.sleep(5)
    statements = parser.get_statements()

    with open('data.txt', 'r', encoding='utf-8') as file:
        statements = json.load(file)

    for statement in statements:
        name_dir = '.\Госуслуги' + '\\' + statement['number']
        if statement['status'] == 'Услуга оказана' and create_dir(name_dir):
            pass




if __name__ == '__main__':
    main()
