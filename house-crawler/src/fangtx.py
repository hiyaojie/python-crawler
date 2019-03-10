# coding=utf-8
import json
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time


def store_info():
    output_file_name = 'ftx-2.xlsx'
    df = pd.DataFrame(get_info_from())
    df.to_excel(output_file_name, index=False)


def get_detail_from(url):
    content = requests.get(url)

    soup = BeautifulSoup(content.text, 'lxml')

    phone = ''

    if soup.select('p.text_phone'):
        phone = str(soup.select('p.text_phone')[0].get_text()).replace(' ', '')
    elif soup.select('div.tjcont-jjr-line2'):
        phone = str(soup.select('div.tjcont-jjr-line2')[0].get_text()).replace(' ', '')
    else:
        pass

    detail_info = {
        'phone': phone,
        'type': soup.select('div.tt')[1].get_text(),
        'area': soup.select('div.tt')[2].get_text()
    }

    return detail_info


def get_info_from():
    # url = 'https://sz.zu.fang.com/house-a089-b02095/g21/'
    url = 'https://sz.zu.fang.com/house-a089-b02095/g21-i32/'

    host = 'https://sz.zu.fang.com'

    content = requests.get(url)

    soup = BeautifulSoup(content.text, 'lxml')

    house_detail_list = []

    for item in soup.select('dd.info'):
        href = item.select('a')[0].get('href')
        title = item.select('p')[0].get_text()
        des = item.select('p')[1].get_text()
        location = item.select('p')[2].get_text()
        price = item.select('span.price')[0].get_text()

        house_info = {
            'href': host + href,
            'title': title,
            'des': str(des).replace(' ', ''),
            'location': location,
            'price': price
        }

        detail_info = {}
        detail_info.update(house_info)
        detail_info.update(get_detail_from(host + href))

        house_detail_list.append(detail_info)

    return house_detail_list


if __name__ == '__main__':
    store_info()
