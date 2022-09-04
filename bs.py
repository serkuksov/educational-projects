import requests
from bs4 import BeautifulSoup
from time import sleep

# params = {'q': 'lesli'}
#
# response = requests.get('https://bookskazan.ru/catalog/', params=params)

# print(response.status_code)
# print(response.headers)
# print(response.content)
# print(response.text)
# with open('test.html', 'w', encoding='utf-8') as f:
#     f.write(response.text)

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ru,en;q=0.9",
    "Host": "wizemart.ru",
    "Referer": "https://wizemart.ru/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.160 YaBrowser/22.5.1.985 Yowser/2.5 Safari/537.36",
    "X-Amzn-Trace-Id": "Root=1-62ad6cb4-5ae3be6d7420acd4041354d0"
  }

# заходим через сесию
variable = requests.Session()

variable.get('https://wizemart.ru/', headers=headers)

sleep(3)
response = variable.get('https://wizemart.ru/catalog/', allow_redirects=True)
print(response)
if response:
    soup = BeautifulSoup(response.text, 'lxml')
    data = soup.find('div', class_="block item categories_item").find('li')
    print(data.text)
    href = 'https://wizemart.ru' + data.find('a').get('href')
    print(href)
    sleep(3)
def get_straniz(href):
    response = variable.get(href, allow_redirects=True)
    print(response)
    if response:
        soup = BeautifulSoup(response.text, 'lxml')
        data = soup.find('ul', class_="pro-list-wrap pro-box").find('h3')
        print(data.text)
        href_tovar = 'https://wizemart.ru' + data.find('a').get('href')
        print(href_tovar)
        href_next = 'https://wizemart.ru' + soup.find('div', class_="pager").find('li', class_='p-next').find('a').get('href')
        print(href_next)
        sleep(1)
        if href_next:
            get_straniz(href_next)
get_straniz(href)