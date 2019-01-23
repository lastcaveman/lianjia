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
from model import Houses

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

    return (r.json())


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


def get_allchengjiao(payload, limit_offset=0):
    url = 'https://app.api.lianjia.com/house/chengjiao/searchv2'
    payload['limit_offset']=str(limit_offset)
    content = get_data(url, payload, method='GET')
    if content['data']['total_count'] ==0:
        return []
    elif limit_offset > content['data']['total_count'] - 20 or limit_offset==2000:
        return content['data']['list']
    else: 
        return content['data']['list'] + get_allchengjiao(payload, limit_offset+20)

class District:
    city_id = 0
    district_id = 0
    district_quanpin = ''
    district_name = ''
    bizcircles = []

    def __init__(self, district, city_id):
        self.city_id = city_id

        if district == None:
            raise ValueError("\"" + district + "\"" +
                             " : it isn't a district.")
        else:
            self.district_id = district['district_id']
            self.district_quanpin = district['district_quanpin']
            self.district_name = district['district_name']
        for bizcircle in district['bizcircle']:
            self.bizcircles.append(Bizcircle(bizcircle, self.city_id))

    def get_chengjiao(self):
        url = 'https://app.api.lianjia.com/house/chengjiao/searchv2'
        payload = {
            'channel': 'sold',
            'city_id': str(self.city_id),
            'condition': '',
            'limit_count': '20',
            'limit_offset': '0',
            'condition': self.district_quanpin,
        }
        content = get_data(url, payload, method='GET')
        chengjiao = []
        if content['data']['total_count'] > 2000:
            for bizcircle in self.bizcircles:
                chengjiao = chengjiao + bizcircle.get_chengjiao()
            return chengjiao
        else:
            return get_allchengjiao(payload,0)

class Bizcircle:
    city = 0
    bizcircle_id = 0
    bizcircle_quanpin = ''
    bizcircle_name = ''

    def __init__(self, bizcircle, city_id):
        self.city_id = city_id
        if bizcircle == None:
            raise ValueError("\"" + bizcircle + "\"" +
                             " : it isn't a bizcircle.")
        else:
            self.bizcircle_id = bizcircle['bizcircle_id']
            self.bizcircle_quanpin = bizcircle['bizcircle_quanpin']
            self.bizcircle_name = bizcircle['bizcircle_name']

    def get_chengjiao(self):
        url = 'https://app.api.lianjia.com/house/chengjiao/searchv2'
        payload = {
            'channel': 'sold',
            'city_id': str(self.city_id),
            'condition': '',
            'limit_count': '20',
            'limit_offset': '0',
            'condition': self.bizcircle_quanpin,
        }
        print(self.bizcircle_quanpin)
        content = get_data(url, payload, method='GET')
        chengjiao = []
        # print(content)
        print(content['data']['total_count'])
        return get_allchengjiao(payload,0)
        # if content['data']['total_count']>2000:
        # for bizcircle in self.bizcircles:
        # bizcircle.get_chengjiao(self)
        # chengjiao = chengjiao + bizcircle.get_chengjiao(self)

        # if content['data']['total_count'] > 2000:
        #     for bizcircle in self.bizcircles:
        #         chengjiao = chengjiao + bizcircle.get_chengjiao()
        #     return chengjiao
        # else:
        #     return get_allchengjiao(payload,0)

class City:
    id = 0
    districts = []

    def __init__(self, id):
        if id == None:
            raise ValueError("\"" + id + "\"" +
                             " : it isn't a id id.")
        else:
            self.id = id

    def get_district(self):
        url = 'https://app.api.lianjia.com/config/config/initData'
        payload = {
            'params': '{{"city_id": {}, "mobile_type": "android", "version": "8.0.1"}}'.format(self.id),
            'fields': '{"city_info": "", "city_config_all": ""}'
        }
        data = get_data(url, payload, method='POST')
        for district in data['data']['city_info']['info'][0]['district']:
            self.districts.append(District(district, self.id))

    def get_chengjiao(self):
        url = 'https://app.api.lianjia.com/house/chengjiao/searchv2'
        payload = {
            'channel': 'sold',
            'city_id': str(self.id),
            'condition': '',
            'limit_count': '20',
            'limit_offset': '0',
        }
        content = get_data(url, payload, method='GET')
        chengjiao = []
        if content['data']['total_count'] > 2000:
            for district in self.districts:
                chengjiao = chengjiao + district.get_chengjiao()
        return chengjiao
class House:
    code = 0
    districts = []

    def __init__(self, id):
        if id == None:
            raise ValueError("\"" + id + "\"" +
                             " : it isn't a id id.")
        else:
            self.id = id

    def get_district(self):
        url='https://app.api.lianjia.com/house/chengjiao/detailpart1'
        payload = {
            'house_code':self.code,
        }
        content = get_data(url, payload, method='GET')
        print(content)

if __name__ == '__main__':

    # city = City(320100)
    # city.get_district()
    # chengjiao = city.get_chengjiao()
    # for v in chengjiao:
    #     try:
    #         house = Houses.get(house_code=v['house_code'], signed_at=v['sign_date'])
    #     except:
    #         house = Houses()
    #         house.house_code = v['house_code']
    #         house.title = v['title']
    #         house.desc = v['desc']
    #         price = 0
    #         if 'price_str' in v.keys():
    #             price = v['price_str']
    #         if 'price_unit' in v.keys():
    #             price = price + v['price_unit']
    #         house.unitprice = v['unit_price_str']
    #         house.signed_at = v['sign_date']
    #         house.save()

