# coding=utf-8
import json
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time


def main():
    print('reading begin...')

    df = pd.DataFrame([])

    output_file_name = 'output-zhilian.xlsx'
    keyword = 'java'

    for page in range(0, 5):
        df_temp = get_info_by_page(page, keyword)
        df = pd.concat([df, df_temp], ignore_index=True)

    df = df.drop_duplicates(subset='SOU_POSITION_ID', keep='first', inplace=False)

    if os.path.exists(output_file_name):
        os.remove(output_file_name)

    df.to_excel(output_file_name, index=False)

    print('read success...')


def get_info_by_page(page, keyword):
    print('reading ' + str(page + 1) + ' page begin...')
    url = 'https://fe-api.zhaopin.com/c/i/sou'

    params = {
        'start': 90 * page,
        'pageSize': '90',
        'cityId': '765',
        'salary': '10001,15000',
        'workExperience': '0103',
        'education': '-1',
        'companyType': '-1',
        'employmentType': '-1',
        'jobWelfareTag': '-1',
        'kw': keyword,
        'kt': '3',
        'at': '614336692cf84336b01268b3b844153f',
        'rt': 'd93899c208764ebe83c99293b94e1248',
        '_v': '0.49083468',
        'userCode': '692270980',
        'x-zp-page-request-id': 'be6dd0fa12bd481a9b96c6550052278c-1551151427718-627218',
    }

    content = requests.get(url, params=params)

    json1 = json.loads(content.text)

    df = pd.DataFrame(json1['data']['results'])

    required_columns = ['SOU_POSITION_ID', 'jobName', 'company', 'salary', 'businessArea', 'jobName', 'positionURL']

    df = df[required_columns]

    df['company_name'] = df.apply(lambda x: x['company']['name'], axis=1)
    df['company_type'] = df.apply(lambda x: x['company']['type']['name'], axis=1)
    df['company_size'] = df.apply(lambda x: x['company']['size']['name'], axis=1)
    df['detail'] = df.apply(lambda x: get_detail_by_url(x['positionURL']), axis=1)

    df = df.drop(columns=['company'])

    print('reading ' + str(page + 1) + ' page success...')

    return df


def get_detail_by_url(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "lxml")

    # time.sleep()

    if soup.select('div.pos-ul')[0]:
        return soup.select('div.pos-ul')[0].get_text()
    else:
        return '暂未查到信息'


if __name__ == '__main__':
    main()
