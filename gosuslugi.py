import logging
import re
import shutil
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


class Parser:
    """Открывает браузер (хром) заходит на сайт Госулуг, проверяет наличие закрытых обращений,
    сравнивает, скачивает файлы"""

    URL = 'https://www.gosuslugi.ru/'
    search_for_days_before = 2

    def __init__(self, login, password, organization=0, timeout=7):
        self.login = login
        self.password = password
        self.organization = organization
        self.timeout = timeout
        try:
            option = ChromeOptions()
            # option.add_argument('dom.webdriver.enabled', False)
            # option.add_argument("--disable-blink-features=AutomationControlled")
            option.add_argument('--log-level=5')
            option.add_argument("--start-maximized")
            option.headless = False
            option.add_experimental_option('prefs', {
                # "download.default_directory": "C:/Users/517/Download", #Change default directory for downloads
                # "download.prompt_for_download": False, #To auto download the file
                # "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True  # It will not show PDF directly in chrome
            })
            self.driver = Chrome(service=Service(ChromeDriverManager().install()), options=option)
            # self.driver.set_window_size(1920, 1080)
            logging.info(f'Браузер открыт')
        except:
            logging.error('Ошибка браузера!!! Веб драйвер не работает')
            raise Exception()
        try:
            self.driver.get(self.URL)
            logging.info(f'Открываю Госуслуги')
            time.sleep(self.timeout)
        except:
            logging.error('Ошибка браузера!!! Не удалось открыть сайт')
            raise Exception()

    def __del__(self):
        self.driver.close()
        self.driver.quit()
        logging.info(f'Браузер закрыт')

    def authorization_user(self):
        try:
            self.driver.find_element(By.XPATH, '//button/span[contains(text(), "Войти")]').click()
            time.sleep(self.timeout)
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
            time.sleep(self.timeout)
        except:
            logging.error('Ошибка парсинга!!! При вводе данных авторизации')
            raise Exception()
        # Проверка на наличия страницы Войти как
        have_account_organization = self.driver.find_elements(By.XPATH, '//div/h3[contains(text(), "Войти как")]')
        if have_account_organization:
            list_organization = self.driver.find_elements(By.XPATH, '//button')
            try:
                try:
                    name = list_organization[self.organization].find_element(By.TAG_NAME, 'h4').text
                    list_organization[self.organization].click()
                    logging.info(f'Выполнен вход как {name}')
                except:
                    logging.error(f'Ошибка!!! Конфиг файл не правильно задан. Оганизации № {self.organization} нет"')
                    list_organization[0].click()
                    name = list_organization[0].find_element(By.TAG_NAME, 'h4').text
                    logging.info(f'Выполнен вход как {name}')
                time.sleep(self.timeout+3)
            except:
                logging.error('Ошибка парсинга!!! При выборе "Войти как"')
                raise Exception()
        elif self.organization > 0:
            logging.error('Ошибка конфигурации!!! Вы не можете войти как организация. '
                          'Таких прав нет у вашего аккаунта')

        logging.info(f'Авторизация прошла успешно')

    def page_scrolling(self):
        self.driver.find_element(By.TAG_NAME, 'html').send_keys(Keys.END)
        logging.info(f'Прокручиваю страницу')

    def search_statements(self):
        while True:
            try:
                if self.organization == 0:
                    statements_driver = self.driver.find_elements(By.XPATH, '//a[contains(@href,"/order/")]')
                    date_messages_final = statements_driver[-1].find_element(By.XPATH, './div/div/div[1]/div/div[2]/div').text
                else:
                    statements_driver = self.driver.find_elements(By.XPATH, '//div[@data-ng-include="feedsListTpl"]/div')
                    date_messages_final = statements_driver[-1].find_element(By.XPATH, './div/a[2]/div/div[1]/div[3]/span').text
                    split_date_messages_final = date_messages_final.split(' ')
                    if split_date_messages_final[0] == 'Сегодня':
                        date_today = datetime.datetime.now().date()
                    elif split_date_messages_final[0] == 'Вчера':
                        date_today = datetime.datetime.now().date() - datetime.timedelta(days=1)
                    else:
                        date_today = datetime.datetime.strptime(split_date_messages_final[0], '%d.%m.%Y').date()
                    date_messages_final = date_today.strftime('%d.%m.%y') + ' в ' + split_date_messages_final[-1]
            except:
                logging.error('Ошибка парсинга!!! Не удалось найти заявки')
                raise Exception()
            control_date = datetime.datetime.now().date() - datetime.timedelta(days=self.search_for_days_before)
            date_messages_final = datetime.datetime.strptime(date_messages_final, '%d.%m.%y в %H:%M').date()
            logging.info(f'Заявки найдены. Дата последнего сообщения на странице: {date_messages_final}')
            if date_messages_final > control_date:
                if self.organization==0:
                    self.page_scrolling()
                else:
                    self.driver.find_element(By.XPATH, '//a[contains(text(), "Показать еще")]').click()
                    time.sleep(self.timeout)
            else:
                break
        return statements_driver

    def get_statements(self):
        self.statements = []
        # time.sleep(800)
        if self.organization == 0:
            self.driver.find_element(By.XPATH, '//a/span[contains(text(), "Заявления")]').click()
        else:
            try:
                self.driver.find_element(By.XPATH, '//div/a[contains(text(), "Заявления")]').click()
            except:
                time.sleep(self.timeout+5)
                self.driver.find_element(By.XPATH, '//div/a[contains(text(), "Заявления")]').click()
                time.sleep(1)
            self.driver.get('https://lk.gosuslugi.ru/notifications?type=ORDER')
            # time.sleep(self.timeout)
            # self.driver.find_element(By.XPATH, '//div[@id="content"]//div/span[contains(text(), "Уведомления")]/..').click()
            # print(v)
            # for i in v:
            #     print(i.get_attribute('innerHTML'))
            #     print(i.text)
        time.sleep(self.timeout)
        statements_driver = self.search_statements()
        try:
            for elm in statements_driver:
                if self.organization == 0:
                    link = elm.get_attribute('href')
                    status = elm.find_element(By.XPATH, './/div[@class="visually-hidden"]').text
                    number = elm.find_element(By.XPATH, './div/div/div[1]/div/div[1]').text.strip()
                    date_messages = elm.find_element(By.XPATH, './div/div/div[1]/div/div[2]').text
                    name = elm.find_element(By.XPATH, './/h4').text
                else:
                    link = elm.find_element(By.XPATH, './/div[@class="visually-hidden"]/..')
                    status = elm.find_element(By.XPATH, './/div[@class="visually-hidden"]').text
                    number = None
                    date_messages = None
                    name = None
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

    def save_statement_faces(self, link, out_dir):
        self.driver.get(link)
        time.sleep(self.timeout)
        try:
            self.driver.find_element(By.XPATH, '//div[contains(text(), "Показать историю")]').click()
            logging.info(f'Нажата кнопка "Показать историю"')
            time.sleep(self.timeout)
        except:
            logging.info(f'Кнопка "Показать историю" отсутствует')
        dict_files = self.downloads_files()
        self.save_text_statement_history(out_dir)
        self.save_file_in_out_dir(out_dir, dict_files)

    def save_text_statement_history(self, out_dir):
        name_file = out_dir + '\\' + 'История заявления.txt'
        statuses = self.driver.find_elements(By.XPATH, '//div[contains(@class,"status")]/p/span[2]')
        text = ''
        for status in statuses:
            list_status = status.text.split('\n')
            text += list_status[1] + ' ' + list_status[0]
            text += '\n'
        with open(name_file, 'w', encoding='utf-8') as file:
            file.write(text)
        logging.info(f'Сохранена история заявления')

    def downloads_files(self):
        if self.organization == 0:
            try:
                groups_docs = self.driver.find_elements(By.XPATH, '//div[@class="files-block"]')
                i = 0
                dict_files = {}
                for docs in groups_docs:
                    list_files = []
                    docs = docs.find_elements(By.XPATH, './/div[@class="file-wrapper"]')
                    for doc in docs:
                        name_doc = doc.find_element(By.XPATH, './div/div[1]/div/div[2]').text
                        if name_doc.split('.')[-1] == 'xml':
                            continue
                        list_files.append(name_doc)
                        doc.find_element(By.XPATH, './/ul[@class="flex-container"]/li/a').click()
                        time.sleep(1)
                    dict_files[i] = list_files
                    i += 1
                time.sleep(15)
                return dict_files
            except:
                logging.error('Ошибка парсинга!!! Не удалось начать скачивать файлы')
                raise Exception()
        else:
            try:
                groups_docs = self.driver.find_elements(By.XPATH, '//div[contains(@class,"order-files")]')
                i = 0
                dict_files = {}
                for docs in groups_docs:
                    list_files = []
                    if i == 0:
                        docs = docs.find_elements(By.XPATH, './/div[@class="file-name"]')
                    elif i == 1:
                        docs = docs.find_elements(By.XPATH, './/div[@class="notification-file-text"]')
                    for doc in docs:
                        name_doc = doc.text
                        link_file = doc.find_element(By.TAG_NAME, 'a').get_attribute('href')
                        if '.xml' in name_doc:
                            continue
                        else:
                            try:
                                name_doc = re.search('[\S]*.(pdf|ods|odt)', name_doc)[0]
                            except:
                                logging.error(f'Ошибка регулярного выражения!!! Не определен тип файла {name_doc}')
                                continue
                        self.driver.get(link_file)
                        time.sleep(1)
                        list_files.append(name_doc)
                    dict_files[i] = list_files
                    i += 1
                return dict_files
            except:
                logging.error('Ошибка парсинга!!! Не удалось начать скачивать файлы')
                raise Exception()

    def save_file_in_out_dir(self, out_dir: str, dict_files: dict):
        for key, name_files in dict_files.items():
            if name_files:
                if self.organization == 0:
                    if key == 0:
                        subfolder = 'Получено'
                    else:
                        subfolder = 'Отправлено'
                else:
                    if key == 1:
                        subfolder = 'Получено'
                    else:
                        subfolder = 'Отправлено'
                new_out_dir = out_dir + '\\' + subfolder
                if not os.path.exists(new_out_dir):
                    os.mkdir(new_out_dir)
                for name_file in name_files:
                    try:
                        path_file = self.get_path_duwnload_file(name_file)
                    except:
                        continue
                    shutil.copy(path_file, new_out_dir)
                    time.sleep(1)
                    try:
                        os.remove(path_file)
                    except:
                        time.sleep(10)
                        os.remove(path_file)
        logging.info(f'Сохранены файлы заявления, если они имелись')

    def get_path_duwnload_file(self, name_file: str):
        try:
            # name_file = name_file.split('.')[0]
            downloads_path = str(Path.home() / "Downloads")
            result = []
            for root, dirs, files in os.walk(downloads_path):
                for f in files:
                    if name_file in f:
                        if 'crdownload' in f:
                            time.sleep(10)
                            f = f.split('.crdownload')[0]
                        path_file = os.path.join(root, f)
                        time_save = os.path.getmtime(path_file)
                        result.append((time_save, path_file))
            result.sort(reverse=True)
            path_file = result[0][1]
            logging.info(f'Путь к скаченомц файлу: {path_file}')
            return path_file
        except:
            logging.error(f'Ошибка!!! Не удалось найти {name_file} в папке загрузок. Файл пропущен')
            raise Exception()

    def click_button(self):
        try:
            self.driver.find_element(By.XPATH, '//span[contains(text(), "История рассмотрения")]').click()
            logging.info(f'Нажата кнопка "История рассмотрения"')
            time.sleep(self.timeout)
        except:
            logging.info(f'Кнопка "История рассмотрения" отсутствует')
        try:
            self.driver.find_element(By.XPATH, '//span[contains(text(), "Все файлы")]').click()
            logging.info(f'Нажата кнопка "Все файлы"')
            time.sleep(self.timeout)
        except:
            logging.info(f'Кнопка "История рассмотрения" отсутствует')
        try:
            self.driver.find_element(By.XPATH, '//span[contains(text(), "Еще")]').click()
            logging.info(f'Нажата кнопка "Еще x файл(-а)"')
            time.sleep(self.timeout)
        except:
            logging.info(f'Кнопка "Еще" отсутствует')

    def save_statement_organizations(self):
        statements_driver = self.driver.find_elements(By.XPATH, '//div[@data-ng-include="feedsListTpl"]/div')
        count_statements = len(statements_driver)
        logging.info(f'Записей к просмотру: {count_statements}')
        self.driver.get('https://lk.gosuslugi.ru/notifications?type=ORDER')
        time.sleep(self.timeout+10)
        for i in range(count_statements):
            statements_driver = self.driver.find_elements(By.XPATH, '//div[@data-ng-include="feedsListTpl"]/div')
            if i >= len(statements_driver):
                while len(statements_driver) < count_statements:
                    self.driver.find_element(By.XPATH, '//a[contains(text(), "Показать еще")]').click()
                    logging.info(f'Нажата кнопка "Показать еще"')
                    time.sleep(self.timeout)
                    statements_driver = self.driver.find_elements(By.XPATH, '//div[@data-ng-include="feedsListTpl"]/div')
                    if i < len(statements_driver):
                        break
            elm = statements_driver[i]
            status = elm.find_element(By.XPATH, './/div[@class="visually-hidden"]').text
            if status == 'Услуга оказана':
                elm.click()
                time.sleep(self.timeout+2)
                logging.info(f'Открываю услугу № {i+1}')
                try:
                    statement = self.driver.find_element(By.XPATH, '//h2/span[2]').text
                except:
                    time.sleep(self.timeout)
                    statement = self.driver.find_element(By.XPATH, '//h2/span[2]').text
                name_dir = '.\Госуслуги' + '\\' + statement
                if not os.path.exists(name_dir):
                    self.click_button()
                    os.mkdir(name_dir)
                    self.save_text_statement_history(name_dir)
                    time.sleep(self.timeout)
                    dict_files = self.downloads_files()
                    self.save_file_in_out_dir(name_dir, dict_files)
                    logging.info(f'Выполнено сохранение услуги: {statement}')
                try:
                    link_back = self.driver.find_element(By.XPATH, '//a[contains(text(), "Вернуться к списку")]').get_attribute('href')
                    self.driver.get(link_back)
                    logging.info(f'Нажата кнопка "Вернуться к списку"')
                    time.sleep(self.timeout+2)
                except:
                    logging.error(f'Кнопка "Вернуться к списку" отсутствует')
                    raise Exception()

def create_dir(name_dir: str):
    if not os.path.exists(name_dir):
        os.mkdir(name_dir)
        return True


def timer(hour: int, function):
    logging.info(f'Жду времени начала сбора данных ({hour}:00)')
    while True:
        # Тайм зона Москва +3
        time_zone = datetime.timezone(datetime.timedelta(hours=3))
        current_time = datetime.datetime.now(time_zone).time()
        if datetime.time(hour) < current_time:
            try:
                function()
            except:
                logging.error(f'Ошибка!!! Что то пошло не так, вторая попытка через 1 минуту')
                time.sleep(60)
                try:
                    function()
                except:
                    logging.error(f'Ошибка!!! Не удачная вторая попытка')
            time_sleep = (24 - current_time.hour) * 3600
            logging.info(f'Засыпаю на {24 - current_time.hour} часов')
            time.sleep(time_sleep)
        else:
            time.sleep(60)


def get_config():
    try:
        with open('config.txt', 'r', encoding='utf-8') as file:
            config = json.load(file)
    except:
        logging.error('Ошибка!!! Не удалось найти или открыть файл конфигурации')
        raise Exception()
    list_config = list(config.keys())
    verification_list_config = [
        "LOGIN",
        "PASSWORD",
        "HOUR_START",
        "TIMEOUT",
        "DEBUGGING",
        "ORGANIZATION"
    ]
    if list_config == verification_list_config:
        return config
    else:
        logging.error('Ошибка!!! В файле конфигурации нет части настроек')
        raise Exception()


def data_parsing(timeout=0):
    create_dir(name_dir='.\Госуслуги')
    config = get_config()
    if timeout>0:
        config['TIMEOUT'] = 15
    parser = Parser(login=config['LOGIN'],
                    password=config['PASSWORD'],
                    organization=int(config['ORGANIZATION']),
                    timeout=int(config['TIMEOUT']))
    parser.authorization_user()
    statements = parser.get_statements()
    if int(config['ORGANIZATION']) == 0:
        for statement in statements:
            name_dir = '.\Госуслуги' + '\\' + statement['number']
            link = statement['link']
            if statement['status'] == 'Услуга оказана' and create_dir(name_dir):
                logging.info(f'Начинаю сохранять заявление: {statement["number"]}')
                parser.save_statement_faces(link, name_dir)
    else:
        parser.save_statement_organizations()


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    handler = logging.FileHandler('log_gosuslugi.txt', 'a', 'utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    root_logger.addHandler(handler)
    if int(get_config()['DEBUGGING']):
        data_parsing()
    else:
        logging.info(f'Парсер запущен')
        HOUR_START = int(get_config()['HOUR_START'])
        timer(hour=HOUR_START, function=data_parsing)


if __name__ == '__main__':
    main()
