from datetime import datetime, date
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.common.by import By
import time
import random
import csv
import re
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from models import *

def recognize_creation_time(creation_time_avito):
    list_param = creation_time_avito.split()
    month_str = {
        'января': '1',
        'февраля': '2',
        'марта': '3',
        'апреля': '4',
        'мая': '5',
        'июня': '6',
        'июля': '7',
        'августа': '8',
        'сентября': '9',
        'октября': '10',
        'ноября': '11',
        'декабря': '12'
    }
    day = list_param[0]
    month = month_str[list_param[1]]
    year = datetime.now().year
    creation_time = datetime.strptime(f"{day}/{month}/{year} {list_param[2]}", "%d/%m/%Y %H:%M")
    return creation_time


def get_ads_from_page(driver, url):
    i = 1
    data = []
    while True:
        link = f'{url}?p={i}'
        driver.get(link)
        page = driver.find_elements(By.CSS_SELECTOR, 'span.pagination-item-JJq_j')[-2].text
        time.sleep(random.randint(6, 9))
        soup = driver.find_elements(By.CSS_SELECTOR, 'div.iva-item-content-rejJg')
        if soup:
            for elm in soup:
                elm_time = elm.find_element(By.CSS_SELECTOR, 'div.date-root-__9qz')
                ActionChains(driver).move_to_element(elm_time).perform()
                name = elm.find_element(By.CSS_SELECTOR, 'h3').text
                href = elm.find_element(By.CSS_SELECTOR, 'div.iva-item-titleStep-pdebR a').get_attribute('href')
                price = elm.find_element(By.CSS_SELECTOR, 'span.price-text-_YGDY').text[:-2]
                price = re.sub(r'\s', '', price)
                type = elm.find_element(By.CSS_SELECTOR, 'div.iva-item-autoParamsStep-WzfS8').text
                adres = elm.find_element(By.CSS_SELECTOR, 'span.geo-address-fhHd0').text
                try:
                    creation_time_avito = elm_time.find_element(By.XPATH, 'span/div').text
                except:
                    creation_time_avito = elm_time.find_element(By.CSS_SELECTOR, 'span.tooltip-tooltip-box-RsJbq div').text
                creation_time = recognize_creation_time(creation_time_avito)
                description = elm.find_element(By.CSS_SELECTOR, 'div.iva-item-descriptionStep-C0ty1').text
                data_elm = {
                'name':name,
                'href': href,
                'price': price,
                'type': type,
                'adres': adres,
                'creation_time': creation_time,
                'description': description
                }
                print(name, href, price, type, adres, creation_time)
                data_elm = writer_db(data_elm)
                data.append(data_elm)
        else:
            break
        print(f'Выполнено {i} из {page}')
        i += 1
    driver.close()
    return data

def writer_db(elm):
    # with db:
    #     db.create_tables([Garage])
    #     Garage.insert_many(data).execute()
    with db:
        garage = Garage.select().where(elm['href'] == Garage.href)
        if garage.exists():
            garage = garage.get()
            if elm['price'] != garage.price:
                garage.new_price = elm['price']
                print('Изменена цена')
            if elm['creation_time'] != garage.creation_time:
                garage.new_creation_time = elm['creation_time']
                print('Изменена дата публикации')
            garage.date_change = date.today()
            garage.date_deletion = None
            garage.save()
            elm = Garage.select().where(elm['href'] == Garage.href).dicts()[0]
        else:
            elm['date_change'] = date.today()
            Garage.insert_many(elm).execute()
            print('Новая запись')
        return elm

def deleted_avito_ads():
    garages = Garage.select().where((Garage.date_change != date.today()) & (Garage.date_deletion == None))
    for garage in garages:
        garage.date_deletion = date.today()
        garage.save()
        print('Запись удалена')

def writer_csv(name, data):
    with open(name, 'w', encoding='utf-8', newline='') as f:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()
        writer.writerows(data)
        print('CSV файл записан')

def main():
    driver = Chrome(service=Service(ChromeDriverManager().install()))
    # купить гараж
    url = 'https://www.avito.ru/kazan/garazhi_i_mashinomesta/prodam-ASgBAgICAUSYA~QQ'
    data = get_ads_from_page(driver, url)
    writer_csv(name='avito.csv', data=data)
    deleted_avito_ads()
    # writer_db(data=data)

if __name__ == '__main__':
    main()
