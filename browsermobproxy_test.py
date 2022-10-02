import time
import pprint
from selenium.webdriver import Chrome, ChromeOptions, DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from browsermobproxy import Server

headers = {
        'authority': 'leroymerlin.ru',
        'accept': '*/*',
        'accept-language': 'ru,en;q=0.9',
        'origin': 'https://leroymerlin.ru',
        'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Yandex";v="22"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.114 Mobile Safari/537.36',
    }
server = Server("browsermob-proxy\\browsermob-proxy-2.1.4-bin\\browsermob-proxy-2.1.4\\bin\\browsermob-proxy.bat")
server.start()
proxy = server.create_proxy()

url = 'https://kazan.leroymerlin.ru/product/stoleshnica-dub-gornyy-120x38x60-sm-ldsp-cvet-korichnevyy-89077701/'
url2 = 'https://bot.sannysoft.com/'
option = ChromeOptions()
# option.add_argument('dom.webdriver.enabled', False)
option.add_argument("--disable-blink-features=AutomationControlled")
option.add_argument('--log-level=5')
option.add_argument("--start-maximized")
option.add_argument('--proxy-server=%s' % proxy.proxy)
option.headless = False
PROXY="localhost:8088"
capabilities = DesiredCapabilities.CHROME.copy()
# capabilities['proxy'] = {
#     "httpProxy": PROXY,
#     "ftpProxy": PROXY,
#     "sslProxy": PROXY,
#     "proxyType": "MANUAL",
#
# }
capabilities['acceptSslCerts'] = True
capabilities['acceptInsecureCerts'] = True
driver = Chrome(service=Service(ChromeDriverManager().install()), options=option, desired_capabilities=capabilities)
proxy.new_har("leroymerlin")
proxy.headers(headers)

driver.set_page_load_timeout(10)
try:
    driver.get(url)
    time.sleep(3)
except:
    pass
finally:
    pprint.pprint(proxy.har)
    driver.quit()
    proxy.close()
    server.stop()



