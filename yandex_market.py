import json
import os
from datetime import datetime, date
from selenium.webdriver import Chrome, ActionChains, ChromeOptions
from selenium.webdriver.common.by import By
import time
import random
import csv
import re
import requests
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from models import *

CATALOG = 'Роботы пылесосы'

def checking_captcha(driver):
    while True:
        ex = driver.title
        # print(ex)
        time.sleep(2)
        if ex != 'Ой!':
            return

def get_ads_from_page(driver, url):
    i = 1
    data = []
    link = f'{url}&p={i}'
    driver.get(link)
    time.sleep(5)
    while True:
        # link = f'{url}&p={i}'
        # driver.get(link)
        checking_captcha(driver)
        # time.sleep(40)
        time.sleep(random.randint(5, 10))
        finish = driver.find_element(By.XPATH, '//*[contains(text(), "Сотрудничество")]')
        ActionChains(driver).move_to_element(finish).perform()
        time.sleep(2)
        soup = driver.find_elements(By.CSS_SELECTOR, 'h3')
        if soup[1]:
            for elm in soup[1:]:

                name = elm.text
                href = elm.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                data_elm = {
                'name':name,
                'href': href
                }
                # print(name)
                data.append(data_elm)
        else:
            break
        try:
            next = driver.find_element(By.XPATH, '//*[contains(text(), "Впер")]')
            ActionChains(driver).move_to_element(next).perform()
            time.sleep(1)
            next.click()
        except:
            print('Все страницы просмотрены!!!!')
            break
        print(f'Выполнено {i}')
        i += 1
    driver.close()
    return data

def writer_csv(name, data):
    with open(name, 'w', encoding='utf-8', newline='') as f:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()
        writer.writerows(data)
        print('CSV файл записан')

def get_photo(name, driver):
    all_photo = driver.find_elements(By.CSS_SELECTOR, f'img[alt="{name}"]')
    for photo in all_photo:
        link_photo = photo.get_attribute('src')
        link_photo = re.sub('/\w*$', '/orig', link_photo)
        save_photo(name_dir=name, link_photo=link_photo)

def create_folder(name_dir):
    check_floder = os.path.isdir(name_dir)
    if not check_floder:
        os.makedirs(name_dir)
        print(f'Создана папка {name_dir}')

def save_photo(name_dir, link_photo):
    name_dir = os.path.join(CATALOG, name_dir)
    create_folder(name_dir)
    img = requests.get(link_photo)
    # name = re.search('img_id\w+.jpeg', link_photo)[0]
    name = link_photo.split('/')[-2]
    name = os.path.join(name_dir, name)
    with open(name, 'wb') as f:
        f.write(img.content)

def get_product(name, link, driver):
    str_params = driver.find_element(By.CSS_SELECTOR, 'div[data-auto="main"] div.cia-vs').get_attribute('data-zone-data')
    dict_params = json.loads(str_params)
    price = dict_params['price']
    if 'oldPrice' in dict_params.keys():
        old_price = dict_params['oldPrice']
    else:
        old_price = None
    data = {
        'name': name,
        'price': price,
        'old_price': old_price,
        'link': link
    }
    name = os.path.join(CATALOG, 'products.csv')
    save_csv(data, name)

def save_csv(data, name):
    fieldnames = data.keys()
    if not os.path.isfile(name):
        with open(name, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, dialect='excel')
            writer.writeheader()
            writer.writerow(data)
    else:
        with open(name, 'a', encoding='utf-8', newline='') as f:
            fieldnames = data.keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames, dialect='excel')
            writer.writerow(data)

def get_specifications(name, driver):
    pass

def parser_product(driver, url):
    driver.get(url)
    checking_captcha(driver)
    name = driver.find_element(By.CSS_SELECTOR, 'h1').text
    name = re.sub('/', '-', name)
    time.sleep(2)
    all_photo = driver.find_elements(By.CSS_SELECTOR, 'span[data-auto="image-gallery-more"]')
    if all_photo:
        all_photo[0].click()
        time.sleep(1)
    get_photo(name, driver)
    get_product(name, url, driver)
    # specifications = driver.find_element(By.XPATH, '//*[contains(text(), "Характеристики")]').click()
    # time.sleep(1)
    # get_specifications(name, driver)



def main(webdriver=None):
    option = ChromeOptions()
    # option.add_argument('dom.webdriver.enabled', False)
    option.add_argument("--disable-blink-features=AutomationControlled")
    # option.headless = True

    driver = Chrome(service=Service(ChromeDriverManager().install()), options=option)
    # driver.get('https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html')
    # time.sleep(100)
    create_folder(CATALOG)
    # # робот пылесосы, сбор сылок
    # url = 'https://market.yandex.ru/catalog--roboty-pylesosy/83798/list?cvredirect=3&rs=eJxNlltuNTQMhAVPgHiqhASsIonvrILlsjw-53L6q1J1Wh8n9nhmnPXzvz_9898f66-vXz3cZs3Q9fsco1K9xFV3yHOluckJmVpEjrH-_vpthi0-xsqOzYiR4YNYp8kYWiZzp-UyndNsdihyzVmctbMsOb0y5JwoPo0vxI65-pDigh1TnaKh6jumxoEjzG-s3Kl4nJiL0o2cKvsjmfNUaaI0E7JLob7U2SV3lbQfCQjSoYwxu_6TtZZmVjfcWUVDtHd6izKqbxC6txmjuHcDOYmqJ8detMTXSD-9xbKiwawDcvgKyjggK0HtE0-a1crK03Z4GiWSvlujKAXeCyVFcsnnOg4ArwMJKUvy9hbeZd0G5pxSIny9Q0CYNkz1ti2L6-RWQrODCfkdnNgC_30imA4KOWmDUUS6xsY4lwyfQ04Wo4ioyM2tEhUDrVPHglyLy9ZjAuVOOzGOBxyP6DTmDkTDNpBcu4Aj0h4is6gpLiJUyAz32MCqlo91wFpaDDi1dpoXU5x2iDB9WU_E9myYy1wOD_Zt1NOTqYN_ADh1T70jXSoj56PycgOXO7cIB38b50hovEbVPdLESqZdJSZo6VOi15Soo5tpiKOv6QNRxawFSvtA0WQ244hUE1hbYuvPr1-A1OM2RhxOSqnf6r3xOaxjMIqewjbEawCazKO1ocakJwy8aUNQZZ00hxJL4dUeqBEDYvtIOyX18VgSbRwjgcecmpm7fIAr_rHkdha0w69NLNB3GHo64zKgf8SaKrGlsInlylVI9swTCvQQzzytmG21xjZFFrBKu8r2CnGAQlRPbIJV3d6aAmjhSBt7cTjzJgOUIjm_jXBZXEFtrRVQnlKs6Q4vLiZtRWH7yCqpdp-TxigtEM4eAHOYwx6SECLNKG5ntUAXwzpZFOy42akRM_McfmpMCpRM2TTGtkHhY3XwFju7FuPtTAj_0Ni2S411KW587B1wESlO9OtaCA_wyq_Hj6TMcYGkycTkT_1eqljuvJVg435Ni0pE9nd3iCJWXYm2uRfEEH_8wabyiAady6xoII7FUzxHfKt-ZnldHXL-h5OO9QtUkLs2cDdYeKlgLXv-uONGOuOtxOYLfrBti6stcK0DyUzouc3uVIKDsiQvlMyd0cgZDu6F2x37RNqsWPR7PIYPDOD6v2Jm29B2FmOEhHJXQ-suO-vSDk5DxEe7wSadr-0WdxvV26S4_vFPGuMH5h9NgU4OrOXObQULU_TODchxND299Uhq1olBXXbukLeJRos4LsuxVtxa7dNBd35pwm4rvLjNKZWlbtfIhQ90OLwjWw0txI4sQVup49NZ4UChn84Qx9KLCBsP46rL1qVNbPssUnzA1ofJPAt8WwlvDAbHJM9q8KTYcSwNT6HG5wiIhgHWtTSFL3R307QddK7x6MpLRb6dhFWKbD6vHMe95-ugbZP982jehc5rJZTMzspjeBC8izkjBVFsP9Y9EuwCbVwqcLtB5b1t6J9dOezu5vZXaPT8rt9UIvc2TA1fyE3X3nmub6dAXq1xXzn8Yb1e7JuT1aZ3CTRBUp_wcd3RmD9M2IhrfDChg4ofaL6uc-0n3H2tgAyUi7guCet4OEX8D30Z9PU%2C&hid=16302536&local-offers-first=0&priceto=30000&glfilter=17354840%3A17354843&glfilter=16328519%3A16328521'
    # data = get_ads_from_page(driver, url)
    # writer_csv(name='y_marcet.csv', data=data)
    # Парсинг объявления
    with open('y_marcet.csv', 'r', encoding='utf-8') as f:
        csv_links = csv.DictReader(f)
        for elm in csv_links:
            link = elm['href']
            data = parser_product(driver, link)
            time.sleep(random.randint(1,2))
    # url1 = 'https://market.yandex.ru/product--robot-pylesos-xiaomi-mi-robot-vacuum-mop-2/1752800728?nid=83798&show-uid=16561717968924751679616001&context=search&priceto=30000&glfilter=17354840%3A17354843&glfilter=16328519%3A16328521&rs=eJxNlltuNTQMhAVPgHiqhASsIonvrILlsjw-53L6q1J1Wh8n9nhmnPXzvz_9898f66-vXz3cZs3Q9fsco1K9xFV3yHOluckJmVpEjrH-_vpthi0-xsqOzYiR4YNYp8kYWiZzp-UyndNsdihyzVmctbMsOb0y5JwoPo0vxI65-pDigh1TnaKh6jumxoEjzG-s3Kl4nJiL0o2cKvsjmfNUaaI0E7JLob7U2SV3lbQfCQjSoYwxu_6TtZZmVjfcWUVDtHd6izKqbxC6txmjuHcDOYmqJ8detMTXSD-9xbKiwawDcvgKyjggK0HtE0-a1crK03Z4GiWSvlujKAXeCyVFcsnnOg4ArwMJKUvy9hbeZd0G5pxSIny9Q0CYNkz1ti2L6-RWQrODCfkdnNgC_30imA4KOWmDUUS6xsY4lwyfQ04Wo4ioyM2tEhUDrVPHglyLy9ZjAuVOOzGOBxyP6DTmDkTDNpBcu4Aj0h4is6gpLiJUyAz32MCqlo91wFpaDDi1dpoXU5x2iDB9WU_E9myYy1wOD_Zt1NOTqYN_ADh1T70jXSoj56PycgOXO7cIB38b50hovEbVPdLESqZdJSZo6VOi15Soo5tpiKOv6QNRxawFSvtA0WQ244hUE1hbYuvPr1-A1OM2RhxOSqnf6r3xOaxjMIqewjbEawCazKO1ocakJwy8aUNQZZ00hxJL4dUeqBEDYvtIOyX18VgSbRwjgcecmpm7fIAr_rHkdha0w69NLNB3GHo64zKgf8SaKrGlsInlylVI9swTCvQQzzytmG21xjZFFrBKu8r2CnGAQlRPbIJV3d6aAmjhSBt7cTjzJgOUIjm_jXBZXEFtrRVQnlKs6Q4vLiZtRWH7yCqpdp-TxigtEM4eAHOYwx6SECLNKG5ntUAXwzpZFOy42akRM_McfmpMCpRM2TTGtkHhY3XwFju7FuPtTAj_0Ni2S411KW587B1wESlO9OtaCA_wyq_Hj6TMcYGkycTkT_1eqljuvJVg435Ni0pE9nd3iCJWXYm2uRfEEH_8wabyiAady6xoII7FUzxHfKt-ZnldHXL-h5OO9QtUkLs2cDdYeKlgLXv-uONGOuOtxOYLfrBti6stcK0DyUzouc3uVIKDsiQvlMyd0cgZDu6F2x37RNqsWPR7PIYPDOD6v2Jm29B2FmOEhHJXQ-suO-vSDk5DxEe7wSadr-0WdxvV26S4_vFPGuMH5h9NgU4OrOXObQULU_TODchxND299Uhq1olBXXbukLeJRos4LsuxVtxa7dNBd35pwm4rvLjNKZWlbtfIhQ90OLwjWw0txI4sQVup49NZ4UChn84Qx9KLCBsP46rL1qVNbPssUnzA1ofJPAt8WwlvDAbHJM9q8KTYcSwNT6HG5wiIhgHWtTSFL3R307QddK7x6MpLRb6dhFWKbD6vHMe95-ugbZP982jehc5rJZTMzspjeBC8izkjBVFsP9Y9EuwCbVwqcLtB5b1t6J9dOezu5vZXaPT8rt9UIvc2TA1fyE3X3nmub6dAXq1xXzn8Yb1e7JuT1aZ3CTRBUp_wcd3RmD9M2IhrfDChg4ofaL6uc-0n3H2tgAyUi7guCet4OEX8D30Z9PU%2C&sku=101744047855&cpc=Ba8gnF-k2u4CFRhL9okSh19zU9Kj7oPPkEaEBckLLmRZDAByGV3F-q8T45Io3v-R2hYyXnO-BthI5TVKgqPtaj36W8KHcacGbr1kPHaTLKUuKxX5SkQk04btkIAnqgyBw9sI7MKAT75RwJG_w4FywVO1FjNy4WdVxxE2qkgFBPatEwl_uat_Txq1Hc_kWCz0&do-waremd5=9VIa64-EPn55Vs0PVUHA2g'
    # url2 = 'https://market.yandex.ru/product--robot-pylesos-ilife-v7s-plus/150947057?cpc=1l0zujA8rIMU4zT2Cd_FCl6bk9gkdppUsP0SVHT_omrx2_Bo7AOYKUvTGAXQsERmz8oGWlChBMlUbW4aRnVVX_19pbirDB_r_dqSn4thdPzsfsClnWtQBjoIRfET6v_lQj2oUtVZ2eb89sFJ60kSbQHPBCjRwRMlBfTADX4u5whCyVLqaJ8_SA%2C%2C&rs=eJxNll2OrbUORAVPgO7TkZCAUTixHTuMgvEyurscJ3vzcI66O1_8U64qZ_78z09___v7_OvHbyN8pkjMnP8bMiIkY4nI_PPHryPT55IVdSRmc7nI8jpasXzsEXaOdtrauviCo8g5xuaPJ6ATY-0MPbdWTn517VtuHpGdy4htJ0kdrbUil8U4t5S_b9dxjnK6jeHeR9Qxgwgd0ILDaqXKmHPTyTy5hkSoJf91z7qGU-dpbCxbohsI6hpp0kYBUBHpL5Iu7zX3PXPnaqhWOkcjGg9SK3VfPEBjhu5zJEl0eu6jDTB5j4ZXzeIXYJlECzCvZAa6Q230XFwBSAMM6mz5jjSVe5b1XfhpO0NGYdVHc1rmrhm_UU8Lk67fxtSs3urapPgh2q2ROaJSPLT4bPhotLzgrn5PlYRnbHmHTbqg1IMkcxlzUchpjts1mX3Q2unCt96FqKsvOsuOaJvp2y3SlhYQKv8p0uJbJHAdIvCzbL6yPgLMqnnetmlLsmnMuHwzcio-SC7m4mt1Nt_Jv-JUhVwVQ6zbHkO3Kgi-tsfmaty2ZxTkRxkTngmUbI4bY_KSw2ECxFopqzmeqqkJNzoiRcCU7Gww30BMTiFbiUFvfTSRzQSR1xull6ouJTcRV-6-xsUht8ZZGqXrI1HfUEduaxLbIWRc_MNWtdOSGlUH2vF4SCYwt37JJoa8kUPfK_RterMEVlfIyyCSCDRal6_qZFiHeHQD6-ReK7cAFMsmUGAHKOYSCJpsHQ2ygLbCjgbZiTeo44CMiBYiW9ctJBmCtG5gajD93SxRfgJzfb1N5j6HPnEItjUaSaAsS-gBQCYP7OkwGWSG-CsfbqY7NnFVyqcm2dn8cLDGUQNAXvl1mYzy0s8ARiT-eYHcZsi-C8lhGsdyTrZlQIXaj3-itgVJm3bAj9TKP1vAODf-cX0rYqF7iu62MY_QNtf6kpHvvFKEJiWUL8tH7rVvlaho4WVXVAZJ6ejeQ76Y-20co0Lcml8P8riqOh604VebOeMe8naKSkkVRv3x4xf-vsIvXNSIU217vAO9uYfdQmb54tCPKVOJf0150-rzcmWRvPpxVCr-TGAOjNfeBDCECnLvwWQoeWkStAkXeoUxa3ytVxjWq5P9oNnzBuR1bZJ5q54hn5km0eBFO-gEc_C3_fSG6WQrANPRsaOcszgJTpsirymsxCBApr3QWW9yWQKKdIn4npdvwcfss_lg7LwqpXRYMu96QAx4WRu2FeGLV5ddDExj6zVs2sQGGkm0WLt7nkrAnuUmfpd6bWH23yNl-UwthFcJhhsnW22NZc9CyWZbPupgwRvS369IK401fyi9bC1b-TSKEetbfcgb3j_nKtscPQCmm7VV3lOGlYANva1OXozgru45PsPOejSEXLAQIXKMpzcsTffTBlpEHvYMm9XBIMMfXVkQFP2xIF5F-bQBIjCgDY8J0ud96BiPhPNQuMtI6q0T9zUAf1jPdl8R-D6Lb9-1UtOP4veb99KvBBg3q-PzQlrwZjyelE1T2TdmqfMbk1fdWcNlFhDiUo8XEQyK2SHR-WQ6cs03YQXqOBsOY2fMANVOXztZwaSUn3CS116_kJQfmIOs_wPqY_Vm&sku=100402417785&do-waremd5=UNhGMyx8oDs2pFzbMh9fOw&priceto=30000&cpa=1&nid=83798'
    # data = parser_product(driver, url1)
    driver.close()
    driver.quit()

if __name__ == '__main__':
    main()