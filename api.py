# -*- coding: utf-8 -*-

import sys
import random
from werkzeug.wrappers import Response
from flask import Flask, jsonify, request
from model import Proxies

app = Flask(__name__)

class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (dict, list)):
            response = jsonify(response)

        return super(JsonResponse, cls).force_type(response, environ)

app.response_class = JsonResponse

@app.route('/')
def index():
    return {
        'code': 200,
        'data': {
            'one': u'get an usable proxy',
            # 'refresh': u'refresh proxy pool',
            'all': u'get all proxy from proxy pool',
            # 'delete?proxy=127.0.0.1:8080': u'delete an unable proxy',
            # 'get_status': u'proxy statistics'
        }
    }

@app.route('/one')
def one():
    proxies = Proxies.select().where(Proxies.https==1).order_by(Proxies.https_time.asc()).limit(88)
    if len(proxies)==0:
        return {
        'code': 404,
        'data': '',
    }
    proxy = random.choice(proxies)
    return {
        'code': 200,
        'data': proxy.url,
    }

@app.route('/all')
def getAll():
    proxies = Proxies.select().where(Proxies.https==1).order_by(Proxies.https_time.asc())
    data = []
    for proxy in proxies:
        data.append(proxy.url)
    return {
        'code': 200,
        'data': data,
    }

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5010)
