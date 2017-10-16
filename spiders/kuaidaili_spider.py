# coding: utf-8

import requests
from bs4 import BeautifulSoup
import redis
import json

base_url = 'http://www.kuaidaili.com/free/inha/'
db = redis.Redis(host='localhost', port=6379, db='ip-pool')


def get_page_data(page_num):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }
    return requests.get(
        '%s/%s' % (base_url, page_num),
        headers=headers,
        proxies={'http': 'http://116.199.2.210:80'})


def get_total_page(page_data):
    soup = BeautifulSoup(page_data, 'html5lib')
    dom_list = soup.select('#listnav a')
    total_page_dom = dom_list[-2]
    return total_page_dom.text


def error_handler(current_page):
    state_code = 0
    while (state_code != 200):
        r = get_page_data(current_page)
        state_code = r.status_code
    return r


def test_survive_ip(ip, port='80', protocol='http'):
    protocol = protocol.lower()
    try:
        requests.get('http://47.52.0.122', proxies={protocol: '%s://%s:%s' % (protocol, ip, port)}, timeout=3)
        print('ip: %s:%s success' % (ip, port))
        return True
    except:
        print('ip: %s:%s error' % (ip, port))
        return False


def get_survive_ip_list(page_data):
    soup = BeautifulSoup(page_data, 'html5lib')
    dom_list = soup.select('#list tr')
    for dom in dom_list[1:]:
        ip = BeautifulSoup(str(dom.select('td[data-title="IP"]')[0]), 'html5lib').select('body')[0].text
        port = BeautifulSoup(str(dom.select('td[data-title="PORT"]')[0]), 'html5lib').select('body')[0].text
        protocol = BeautifulSoup(str(dom.select('td[data-title="类型"]')[0]), 'html5lib').select('body')[0].text
        if test_survive_ip(ip, port, protocol):
            save(ip, port, protocol)


def save(ip, port, protocol):
    value = json.dumps(dict(port=port, protocol=protocol))
    db.set(ip, value)


def deal_page(current_page):
    r = get_page_data(current_page)
    if r.status_code != 200:
        r = error_handler(current_page)
    page_data = r.text
    get_survive_ip_list(page_data)
    return get_total_page(page_data)


def main():
    current_page = 1
    total_page = deal_page(current_page)
    while int(current_page) < int(total_page):
        current_page += 1
        deal_page(current_page)


if __name__ == '__main__':
    main()
