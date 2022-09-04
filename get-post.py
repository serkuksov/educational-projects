import json
import re
import time
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from models import *

headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.160 YaBrowser/22.5.1.985 Yowser/2.5 Safari/537.36",
  }

# variable = requests.Session()
#
# response = variable.get('https://coinmarketcap.com/nft/upcoming/', headers=headers)
# soup = BeautifulSoup(response.text, 'lxml')
# count_elments = soup.find(string=re.compile("Showing")).text
# count_elments = re.search(r'\d+$', count_elments)[0]
#
# response = variable.get(f'https://api.coinmarketcap.com/data-api/v3/nft/upcomings?start=0&limit={count_elments}', headers=headers)
# time.sleep(2)
# data_json = response.json()['data']['upcomings']
# with open('test.txt', 'w', encoding='utf-8') as f:
#     json.dump(data_json, f)

with open('test.txt', 'r', encoding='utf-8') as f:
    data_json = json.load(f)

for elm in data_json[:2]:
    pprint(elm)
fields = ['name', 'twitter', 'preview', 'description', 'discord', 'website', 'platform', 'mintPrice', 'dateTime']
print(fields)
# Coinmarketcap.create_table()
Coinmarketcap.insert_many(data_json, fields=fields).execute()

# with open('index.html', 'w', encoding='utf-8') as f:
#     f.write(response.text)

# with open('index.html', 'r', encoding='utf-8') as f:
#     html = f.read()

def parser_html():
    soup = BeautifulSoup(response.text, 'lxml')
    soup.find('div', class_='table')
    elments = soup.find('div', class_='table').find('tbody').find_all('tr')
    for elm in elments:
        elm_dict = {}
        td = elm.find_all('td')
        td_0 = td[0].get_text(separator='*', strip=True).split('*')
        elm_dict['name'] = td_0[0]
        elm_dict['name_network'] = td_0[1]
        elm_dict['description'] = td_0[2]
        td_1 = td[1].find_all('a')
        elm_dict['link_discord'] = td_1[0].get('href')
        elm_dict['link_twitter'] = td_1[1].get('href')
        elm_dict['link_website'] = td_1[2].get('href')
        td_2 = td[2].find_all('p')[1].text
        elm_dict['datatime'] = td_2.replace(',', '').replace('/', '.')
        td_3 = td[3].find_all('span')[-1].text
        elm_dict['sale'] = re.search(r'\d+.\d+', td_3)
        td_4 = td[4].find_all('img')
        img_list_links = []
        for img in td_4:
            img_list_links.append(img.get('src'))
        elm_dict['img'] = img_list_links
        print(elm_dict)
