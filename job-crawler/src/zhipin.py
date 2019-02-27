# coding=utf-8
import json
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time


def get_info_from_zhipin():
    # TODO:使用装饰器改进打印
    print('reading from boss zhipin begin...')

    # 简单配置
    output_file_name = 'output-zhipin.xlsx'
    keyword = 'java'
    max_page = 10

    # 使用pandas存储数据
    # TODO:使用数据库存储数据
    df = pd.DataFrame([])
    for page in range(1, max_page):
        df_temp = pd.DataFrame(get_info_by_kw_and_page(keyword, page))
        df = pd.concat([df, df_temp], ignore_index=True)

    # 去重操作
    df = df.drop_duplicates(subset='link', keep='first', inplace=False)

    # 改变字段的顺序
    required_columns = ['title', 'name', 'salary', 'detail', 'msg', 'link']
    df = df[required_columns]

    # 如果已经出现就删掉重新生成
    if os.path.exists(output_file_name):
        os.remove(output_file_name)

    # 导出到excel，并去除默认index
    df.to_excel(output_file_name, index=False)

    print('read from boss zhipin success...')


def get_info_by_kw_and_page(keyword, page):
    """
    根据关键字和页码获取数据
    :param keyword:岗位关键字，如java
    :param page:页码
    :return:岗位信息列表
    """

    print('reading ' + str(page) + ' page begin...')
    url = 'https://www.zhipin.com/mobile/jobs.json'

    params = {
        'experience': 104,
        'salary': 4,
        'page': page,
        'city': 101280600,
        'query': keyword
    }

    # 定制一个headers，默认user-agent会被拦截
    headers = {
        'referer': 'https://www.zhipin.com/c101280600/y_4-e_104/?ka=sel-salary-4',
        'user-agent': 'Mozilla/5.0(iPhone;CPUiPhoneOS11_0likeMacOSX)AppleWebKit/604.1.38(KHTML,likeGecko)'
                      'Version/11.0Mobile/15A372Safari/604.1'
    }

    content = requests.get(url, params=params, headers=headers)

    soup = BeautifulSoup(json.loads(content.text)['html'], 'lxml')

    items = soup.select('li.item')

    host = 'https://www.zhipin.com'

    job_detail_list = []

    for item in items:
        link = host + item.select('a')[0].get('href')
        job_detail = {
            'link': link,
            'title': item.select('h4')[0].get_text(),
            'salary': item.select('span.salary')[0].get_text(),
            'name': item.select('div.name')[0].get_text(),
            'msg': item.select('div.msg')[0].get_text(),
            'detail': get_detail_by_url(link)
        }
        job_detail_list.append(job_detail)

    print('reading ' + str(page) + ' page success...')

    return job_detail_list


def get_detail_by_url(url):
    headers = {
        'referer': 'https://www.zhipin.com/c101280600/y_4-e_104/?ka=sel-salary-4',
        'user-agent': 'Mozilla/5.0(iPhone;CPUiPhoneOS11_0likeMacOSX)AppleWebKit'
                      '/604.1.38(KHTML,likeGecko)Version/11.0Mobile/15A372Safari/604.1'
    }
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'lxml')
    if soup.select('div.job-sec div.text'):
        return soup.select('div.job-sec > div.text')[0].get_text().strip()
    else:
        return "暂未查到信息"


if __name__ == '__main__':
    get_info_from_zhipin()
