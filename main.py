# coding: utf-8

import requests

try:
    requests.get('http://103.210.236.185:8080/', proxies={'https': 'https://113.108.130.210:808'})
    print('ok')
except:
    print('error')
