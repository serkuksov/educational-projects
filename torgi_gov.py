from time import sleep
from pprint import pprint
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


def filter_params(driver, type_property=None, region=None, city=None, delay=1):
    inputs = driver.find_elements(By.XPATH, '//a[@title="Выбрать"]')
    if type_property:
        inputs[0].click()
        sleep(delay)
        input_type = driver.find_element(By.XPATH, f'//span[contains(text(), "{type_property}")]/preceding::input[1]')
        input_type.click()
        sleep(delay)
        button = driver.find_element(By.XPATH, f'//ins[contains(text(), "Выбрать")]')
        button.click()
        sleep(delay)
    if region:
        inputs[1].click()
        sleep(delay)
        input_region = driver.find_element(By.XPATH, '//input[@name="container1:level1"]')
        input_region.click()
        input_region.send_keys(region)
        driver.find_element(By.XPATH, f'//label[contains(text(), "Субъект РФ:")]').click()
        sleep(delay)
        if city:
            input_city = driver.find_element(By.XPATH, '//input[@name="container2:level2"]')
            input_city.click()
            input_city.send_keys(city)
            sleep(delay)
        button = driver.find_element(By.XPATH, f'//ins[contains(text(), "Выбрать")]')
        button.click()
        sleep(delay)
    button = driver.find_element(By.XPATH, f'//ins[contains(text(), "Поиск")]')
    button.click()
    sleep(4)


def get_driver():
    option = ChromeOptions()
    # option.add_argument('dom.webdriver.enabled', False)
    # option.add_argument("--disable-blink-features=AutomationControlled")
    option.headless = True
    driver = Chrome(service=Service(ChromeDriverManager().install()), options=option)
    url = 'https://torgi.gov.ru/lotSearch2.html?bidKindId=13'
    driver.get(url)
    return driver


def get_list_of_trades(driver):
    str_table = driver.find_elements(By.XPATH, '//div[@class="scrollx"]/*/tbody/tr')
    list_of_trades = []
    for elm in str_table:
        column = elm.find_elements(By.XPATH, 'td')
        link = column[0].find_element(By.XPATH, '*//a[@title="Просмотр"]').get_attribute('href')
        discription = column[3].text
        prise = column[4].text
        address = column[5].text.split(',')
        region = address[0]
        if len(address) > 1:
            city = address[1]
        else:
            city = None
        dict_params = {
            'link': link,
            'discription': discription,
            'prise': prise,
            'region': region,
            'city': city
        }
        list_of_trades.append(dict_params)
    return list_of_trades


def main():
    type_property = 'Гараж'
    region = 'Татарстан'
    city = 'Казань'
    try:
        driver = get_driver()
        filter_params(driver, type_property, region, city)
        list_of_trades = get_list_of_trades(driver)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
    #TODO нужно довать тип объявления в выдачу
    pprint(list_of_trades)

if __name__ == '__main__':
    main()
