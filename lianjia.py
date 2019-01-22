# -*- coding: utf-8 -*-
import os
import sys
import getopt
import urllib.parse
import urllib.request
import copy
import hashlib
import codecs
import requests
import re
from six.moves import queue as Queue
from threading import Thread
import time
import json
import datetime
from bs4 import BeautifulSoup
import pandas as pd
from peewee import *
import pymysql
import base64
import logging

HEADERS = {
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'upgrade-insecure-requests': '1',
    'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
    'Cookie': 'tt_webid=6634768059273332225; _ga=GA1.3.1307784653.1544777323; _gid=GA1.3.720099781.1544777323; _gat=1',
}


def get_data(url, payload, method='GET', session=None):
    payload['request_ts'] = int(time.time())

    headers = {
        'User-Agent': 'HomeLink7.7.6; Android 7.0',
        'Authorization': get_token(payload)
    }
    if session:
        if method == 'GET':
            r = session.get(url, params=payload, headers=headers)
        else:
            r = session.post(url, data=payload, headers=headers)
    else:
        if method == 'GET':
            r = requests.get(url, params=payload, headers=headers)
        else:
            r = requests.post(url, params=payload,
                              data=payload, headers=headers)

    return parse_data(r)


def parse_data(response):
    return response.content.decode("utf-8")
    as_json = response.json()
    if as_json['errno']:
        # 发生了错误
        raise Exception('请求出错了: ' + as_json['error'])
    else:
        return as_json['data']


def get_token(params):
    data = list(params.items())
    data.sort()

    token = '7df91ff794c67caee14c3dacd5549b35'
    for entry in data:
        token += '{}={}'.format(*entry)

    token = hashlib.sha1(token.encode()).hexdigest()
    token = '{}:{}'.format('20161001_android', token)
    token = base64.b64encode(token.encode()).decode()

    return token


class District:
    district_id = 0
    district_quanpin = ''
    district_name = ''

    def __init__(self, district):
        if district == None:
            raise ValueError("\"" + district + "\"" +
                             " : it isn't a district.")
        else:
            self.district_id = district.district_id
            self.district_quanpin = district.district_quanpin
            self.district_name = district.district_name


class Bizcircle:
    bizcircle_id = 0
    bizcircle_quanpin = ''
    bizcircle_name = ''

    def __init__(self, bizcircle):
        if bizcircle == None:
            raise ValueError("\"" + bizcircle + "\"" +
                             " : it isn't a bizcircle.")
        else:
            self.bizcircle_id = bizcircle.bizcircle_id
            self.bizcircle_quanpin = bizcircle.bizcircle_quanpin
            self.bizcircle_name = bizcircle.bizcircle_name


class City:
    city_id = 0

    def __init__(self, city_id):
        if city_id == None:
            raise ValueError("\"" + city_id + "\"" +
                             " : it isn't a city_id id.")
        else:
            self.city_id = city_id

    def get_district(self):
        url = 'https://app.api.lianjia.com/config/config/initData'
        payload = {
            'params': '{{"city_id": {}, "mobile_type": "android", "version": "8.0.1"}}'.format(self.city_id),
            'fields': '{"city_info": "", "city_config_all": ""}'
        }
        data = get_data(url, payload, method='POST')
        # district


if __name__ == '__main__':
    city = City(city_id=110000)
    city.get_district()
