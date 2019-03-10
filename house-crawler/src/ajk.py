# coding=utf-8
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree
import time

headers = {
    'cookie': 'sessid=F3C5048F-5EFC-7DC2-D706-171B3F342202; aQQ_ajkguid=E6473576-0CFA-547A-EF66-9729C7E5C2C4; lps=http%3A%2F%2Fwww.anjuke.com%2F%7Chttps%3A%2F%2Fwww.sogou.com%2Flink%3Furl%3DDSOYnZeCC_q7j7wj5mgOqD1S3J7oRWO3; ctid=18; twe=2; __xsptplusUT_8=1; 58tj_uuid=eba8ad5e-f054-41aa-b36a-c28a5c2a062e; init_refer=https%253A%252F%252Fwww.sogou.com%252Flink%253Furl%253DDSOYnZeCC_q7j7wj5mgOqD1S3J7oRWO3; new_uv=1; als=0; new_session=0; wmda_uuid=4007ce9d02b60083c9b2c096f2e5dc8a; wmda_new_uuid=1; wmda_session_id_6289197098934=1545017039830-dffe50e6-70d0-7706; wmda_visited_projects=%3B6289197098934; __xsptplus8=8.1.1545017036.1545017044.3%233%7Cwww.sogou.com%7C%7C%7C%7C%23%23k4--hgzAYsNToYCPD0_3M1ppGohhWYm5%23',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
}


def store_info():
    output_file_name = 'ajk.xlsx'
    df = pd.DataFrame(get_from_ajk())
    df.to_excel(output_file_name, index=False)


def get_detail_from(url):
    time.sleep(3)

    print('正在获取'+url)
    content = requests.get(url,headers=headers)

    soup = BeautifulSoup(content.text, 'lxml')

    detail = {
        'price': soup.select('div.title-basic-info > span')[0].get_text(),
        'type': soup.select('div.title-basic-info > span')[1].get_text(),
        'area': soup.select('div.title-basic-info > span')[2].get_text(),
        'phone': get_ajax_phone(url)
    }

    return detail


def get_from_ajk():
    url = 'https://sz.zu.anjuke.com/fangyuan/shiyan/fx1-p1/'

    content = requests.get(url,headers=headers)

    soup = BeautifulSoup(content.text, 'lxml')

    house_detail_list = []

    for item in soup.select('div.zu-info'):
        href = item.select('a')[0].get('href')
        title = item.select('a')[0].get_text()
        des = item.select('p')[0].get_text()
        location = str(item.select('address.details-item')[0].get_text()).replace(' ', '')

        basic = {
            'href': href,
            'title': title,
            'des': des,
            'location': location
        }

        house_detail = {}
        house_detail.update(basic)
        house_detail.update(get_detail_from(href))
        house_detail_list.append(house_detail)

    return house_detail_list


def get_ajax_phone(j):
    # 定制请求头，必须保存cookie信息，否则无法获取手机号
    headers = {
        'cookie': 'sessid=F3C5048F-5EFC-7DC2-D706-171B3F342202; aQQ_ajkguid=E6473576-0CFA-547A-EF66-9729C7E5C2C4; lps=http%3A%2F%2Fwww.anjuke.com%2F%7Chttps%3A%2F%2Fwww.sogou.com%2Flink%3Furl%3DDSOYnZeCC_q7j7wj5mgOqD1S3J7oRWO3; ctid=18; twe=2; __xsptplusUT_8=1; 58tj_uuid=eba8ad5e-f054-41aa-b36a-c28a5c2a062e; init_refer=https%253A%252F%252Fwww.sogou.com%252Flink%253Furl%253DDSOYnZeCC_q7j7wj5mgOqD1S3J7oRWO3; new_uv=1; als=0; new_session=0; wmda_uuid=4007ce9d02b60083c9b2c096f2e5dc8a; wmda_new_uuid=1; wmda_session_id_6289197098934=1545017039830-dffe50e6-70d0-7706; wmda_visited_projects=%3B6289197098934; __xsptplus8=8.1.1545017036.1545017044.3%233%7Cwww.sogou.com%7C%7C%7C%7C%23%23k4--hgzAYsNToYCPD0_3M1ppGohhWYm5%23',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
    }

    # 随便获取一个详情界面的链接吧
    # j = "https://sz.zu.anjuke.com/fangyuan/1286839211"

    # 获取网页源码
    xq_link = requests.get(j, headers=headers)
    xq_html = etree.HTML(xq_link.text, etree.HTMLParser())

    # 利用正则获取参数
    # 匹配出参数所在的代码
    phone_data1 = xq_html.xpath('/html/body/div[3]/script[9]/text()')
    # 第一个参数
    regexp = r"broker_id:\'(.*?)\',"
    res1 = re.findall(regexp, phone_data1[0])
    req1 = res1[0]
    # print(req1[0])
    # 第二个参数
    regexp = r"token: \'(.*?)\',"
    res2 = re.findall(regexp, phone_data1[0])
    req2 = res2[0]
    # print(req2[0])
    # 第三个参数，发现这个参数是房屋编号，便使用xpath提取出来吧
    phone_data3 = xq_html.xpath('//*[@id="houseCode"]/text()')
    regexp = r'：(.*?)，'
    res3 = re.findall(regexp, phone_data3[0])
    req3 = res3[0]
    # print(req3)

    # 拼凑获取手机号的url
    url = "https://hz.zu.anjuke.com/v3/ajax/getBrokerPhone/?broker_id={}&token={}&prop_id={}"
    # 将刚才的参数填到url中
    phone_url = url.format(req1, req2, req3)
    # 获取手机号
    data1 = requests.get(phone_url, headers=headers)
    # print(data1.text)
    # 手机号码的正则匹配公式
    regexp = r'"val":"(.*?)"}'
    # 正则匹配
    res = re.findall(regexp, data1.text)
    phone = res[0]
    return phone


if __name__ == '__main__':
    print(store_info())
