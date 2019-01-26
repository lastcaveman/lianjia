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
import threading
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
from model import Chengjiaos
from model import Locations
from model import Communities
from model import Logs

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
        'Connection': 'close',
        'Authorization': get_token(payload)
    }


    q = requests.session()
    q.keep_alive = False
    q.adapters.DEFAULT_RETRIES = 30 
    if method == 'GET':
        r = q.get(url, params=payload, headers=headers)
    else:
        r = q.post(url, params=payload, data=payload, headers=headers)

    # if session:
    #     if method == 'GET':
    #         r = session.get(url, params=payload, headers=headers)
    #     else:
    #         r = session.post(url, data=payload, headers=headers)
    # else:
    #     if method == 'GET':
    #         r = requests.get(url, params=payload, headers=headers)
    #     else:
    #         r = requests.post(url, params=payload, data=payload, headers=headers)
    log = Logs()
    log.query = r.request.url
    log.result = r.content
    log.save()
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
    payload['limit_offset'] = str(limit_offset)
    content = get_data(url, payload, method='GET')
    if content['data']['total_count'] == 0:
        return []
    elif limit_offset > content['data']['total_count'] - 20 or limit_offset == 2000:
        return content['data']['list']
    else:
        return content['data']['list'] + get_allchengjiao(payload, limit_offset+20)


def get_all_info(url, payload, limit_offset=0):
    payload['limit_offset'] = str(limit_offset)
    content = get_data(url, payload, method='GET')
    if 'total_count' not in content['data'].keys():
        print(content)
        return []
    if content['data']['total_count'] == 0:
        return []
    elif limit_offset > content['data']['total_count'] - 20 or limit_offset == 2000:
        return content['data']['list']
    else:
        return content['data']['list'] + get_all_info(url, payload, limit_offset+20)


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
            try:
                location = Locations.get(
                    level='district', adcode=self.district_id)
            except:
                location = Locations()
                location.adcode = district['district_id']
                location.name = district['district_name']
                location.quanpin = district['district_quanpin']
                location.parent = city_id
                location.level = 'district'
                location.save()
        if 'bizcircle' in district:
            for bizcircle in district['bizcircle']:
                self.bizcircles.append(
                    Bizcircle(bizcircle, self.city_id, self.district_id))

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
            return get_allchengjiao(payload, 0)


class Bizcircle:
    city = 0
    bizcircle_id = 0
    bizcircle_quanpin = ''
    bizcircle_name = ''

    def __init__(self, bizcircle, city_id, district_id):
        self.city_id = city_id
        if bizcircle == None:
            raise ValueError("\"" + bizcircle + "\"" +
                             " : it isn't a bizcircle.")
        else:
            self.bizcircle_id = bizcircle['bizcircle_id']
            self.bizcircle_quanpin = bizcircle['bizcircle_quanpin']
            self.bizcircle_name = bizcircle['bizcircle_name']

            try:
                location = Locations.get(
                    level='bizcircle', adcode=self.bizcircle_id)
            except:
                location = Locations()
                location.adcode = bizcircle['bizcircle_id']
                location.name = bizcircle['bizcircle_name']
                location.quanpin = bizcircle['bizcircle_quanpin']
                location.parent = district_id
                location.level = 'bizcircle'
                location.save()

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
        content = get_data(url, payload, method='GET')
        chengjiao = []
        return get_allchengjiao(payload, 0)


class Poi:

    citys = []

    def load(self):
        url = 'https://app.api.lianjia.com/config/config/initData'
        payload = {
            'params': '{"city_id":"","mobile_type": "android", "version": "8.0.1"}',
            'fields': '{"city_info": "", "city_config_all": ""}'
        }
        data = get_data(url, payload, method='POST')

        for v in data['data']['city_config_all']['list']:
            try:
                location = Locations.get(level='city', adcode=v['city_id'])
            except:
                location = Locations()
                location.level = 'city'
                location.adcode = v['city_id']
                location.name = v['city_name']
                location.quanpin = v['abbr']
                location.parent = 0
                location.save()
            self.citys.append(City(v['city_id']))


class City:
    city_id = 0
    districts = []

    def __init__(self, id):
        if id == None:
            raise ValueError("\"" + id + "\"" +
                             " : it isn't a id id.")
        else:
            self.city_id = id
            self.load()

    def load(self):
        url = 'https://app.api.lianjia.com/config/config/initData'
        payload = {
            'params': '{{"city_id": {}, "mobile_type": "android", "version": "8.0.1"}}'.format(self.city_id),
            'fields': '{"city_info": "", "city_config_all": ""}'
        }
        data = get_data(url, payload, method='POST')
        for district in data['data']['city_info']['info'][0]['district']:
            self.districts.append(District(district, self.city_id))

    def get_chengjiao(self):
        url = 'https://app.api.lianjia.com/house/chengjiao/searchv2'
        payload = {
            'channel': 'sold',
            'city_id': str(self.city_id),
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
    city_id = None
    community_id = None
    price = None
    unitprice = None
    bedroom = None
    hall = None
    chengjiao_detail = None

    def __init__(self, code):
        if code == None:
            raise ValueError("\"" + code + "\"" +
                             " : it isn't a id id.")
        else:
            self.code = code

    def update_chengjiao(self):
        url = 'https://app.api.lianjia.com/house/chengjiao/detailpart1'
        payload = {
            'house_code': self.code,
        }
        content = get_data(url, payload, method='GET')

        # print(content)

        self.city_id = content['data']['basic_info']['city_id']
        self.community_id = content['data']['basic_info']['community_id']
        self.price = content['data']['basic_info']['price']
        self.unitprice = content['data']['basic_info']['unit_price']
        self.bedroom = content['data']['basic_info']['blueprint_bedroom_num']
        self.hall = content['data']['basic_info']['blueprint_hall_num']
        self.chengjiao_detail = json.dumps(content['data'], ensure_ascii=False)

        source_price = None
        period = None
        follows = None
        check = None
        view = None
        change_price = None

        history_i = 0
        for history in content['data']['deal_info']['history']['list']:
            if history_i == 0 and 'review' in content['data']['deal_info'].keys():
                for review in content['data']['deal_info']['review']['list']:
                    if review['name'].find('挂牌价格') >= 0:
                        source_price = review['value']
                    if review['name'].find('成交周期') >= 0:
                        if review['value'] == '暂无':
                            period = None
                        else:
                            period = int(review['value'])
                    if review['name'].find('关注') >= 0:
                        follows = int(review['value'])
                    if review['name'].find('带看') >= 0:
                        check = int(review['value'])
                    if review['name'].find('浏览') >= 0:
                        view = int(review['value'])
                    if review['name'].find('调价') >= 0:
                        change_price = int(review['value'])
            else:
                source_price = None
                period = None
                follows = None
                check = None
                view = None
                change_price = None
            history_i = history_i+1
            signed_at = history['desc'][history['desc'].find(
                '，')+1:].replace('成交', '')
            try:
                chengjiao = Chengjiaos.get(
                    house_code=self.code, signed_at=signed_at)
            except:
                chengjiao = Chengjiaos()
                chengjiao.house_code = self.code
                chengjiao.signed_at = signed_at
                chengjiao.price = history['price']
                chengjiao.unit_price = history['desc'][0:history['desc'].find(
                    '，')].replace('单价', '')
                chengjiao.source_price = source_price
                chengjiao.period = period
                chengjiao.follows = follows
                chengjiao.check = check
                chengjiao.view = view
                chengjiao.change_price = change_price

                if chengjiao.price != '暂无价格' and chengjiao.source_price != None:
                    chengjiao.price_change = float(chengjiao.price.replace(
                        '万', '')) - float(chengjiao.source_price)
                chengjiao.save()


def threadingloadss(v):
    print(v)
    v = Houses.get(id=v)
    house = House(v.house_code)
    house.update_chengjiao()
    v.city = house.city_id
    v.community = house.community_id
    v.price = house.price
    v.unitprice = house.unitprice
    v.bedroom = house.bedroom
    v.hall = house.hall
    v.chengjiao_detail = house.chengjiao_detail
    v.save()
    # house = House(house_code)
    # house.update_chengjiao()

# t= threading.Thread(target=f1,args=(111,112))#创建线程
# t.setDaemon(True)#设置为后台线程，这里默认是False，设置为True之后则主线程不用等待子线程
# t.start()#开启线程

# t = threading.Thread(target=f1, args=(111, 112))
# t.start()

# t = threading.Thread(target=f1, args=(111, 112))
# t.start()


def load_community(adcode):
    print(adcode)
    # bizcircle = Locations.get(adcode=adcode)
    # district = Locations.get(adcode=bizcircle.parent)
    city = Locations.get(adcode=adcode)

    url = 'http://app.api.lianjia.com/house/community/search'
    payload = {
        'city_id': city.adcode,
        'limit_count': '20',
        'limit_offset': '0',
    }
    communities = []
    content = get_data(url, payload, method='GET')
    if 'total_count' not in content['data'].keys():
        return
    if content['data']['total_count'] < 2000:
        communities = get_all_info(url, payload)
    else:
        districts = Locations.select().where(Locations.level == 'district',
                                             Locations.parent == city.adcode)
        for district in districts:
            payload = {
                'district_id': str(district.adcode),
                'district_name': str(district.name),
                'city_id': city.adcode,
                'limit_count': '20',
                'limit_offset': '0',
            }
            content = get_data(url, payload, method='GET')
            if 'total_count' not in content['data'].keys():
                continue
            if content['data']['total_count'] < 2000:
                communities = communities + get_all_info(url, payload)
            else:
                bizcircles = Locations.select().where(Locations.level == 'bizcircle',
                                                      Locations.parent == district.adcode)
                for bizcircle in bizcircles:
                    payload = {
                        'bizcircle_id': str(bizcircle.adcode),
                        'bizcircle_name': str(bizcircle.name),
                        'city_id': city.adcode,
                        'limit_count': '20',
                        'limit_offset': '0',
                    }
                    content = get_data(url, payload, method='GET')
                    if 'total_count' not in content['data'].keys():
                        continue
                    if content['data']['total_count'] < 2000:
                        communities = communities + get_all_info(url, payload)
                    else:
                        print(bizcircle)
                        print('> 2000')

    communities = get_all_info(url, payload)
    for v in communities:
        try:
            community = Communities.get(source=v['community_id'])
        except:
            community = Communities()
            community.source = v['community_id']
        community.name = v['community_name']
        community.city_name = city.name
        if 'district_name' in v.keys():
            community.district_name = v['district_name']
        if 'bizcircle_name' in v.keys():
            community.bizcircle_name = v['bizcircle_name']
        community.avg_unit_price = v['avg_unit_price']
        community.ershoufang_source_count = v['ershoufang_source_count']
        community.save()


if __name__ == '__main__':



    poi = Poi()
    poi.load()

    for city in poi.citys:
        chengjiao = city.get_chengjiao()
        for v in chengjiao:
            try:
                house = Houses.get(house_code=v['house_code'], signed_at=v['sign_date'])
            except:
                house = Houses()
                house.house_code = v['house_code']
                house.title = v['title']
                house.desc = v['desc']
                price = 0
                if 'price_str' in v.keys():
                    price = v['price_str']
                if 'price_unit' in v.keys():
                    price = price + v['price_unit']
                house.unitprice = v['unit_price_str']
                house.signed_at = v['sign_date']
                house.save()

    citys = Locations.select().where(Locations.level == 'city')
    for v in citys:
        while threading.activeCount() > 20:
            # print('there are', threading.activeCount(), 'threads running')
            time.sleep(2)
        threading.Thread(target=load_community, args=(v.adcode,)).start()


    houses = Houses.select().where(Houses.city == None, Houses.id >= 1)
    for v in houses:
        while threading.activeCount() > 40:
            print('there are', threading.activeCount(), 'threads running')
            time.sleep(0.05)

        print('there are', threading.activeCount(), 'threads running')
        t = threading.Thread(target=threadingloadss, args=(v.id,))  # 创建线程
        t.start()


