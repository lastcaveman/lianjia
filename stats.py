# -*- coding: utf-8 -*-
import os
import sys
from model import Houses
from model import Chengjiaos
from model import Locations
from model import Communities
from model import Logs
from model import Stats
import datetime
import time


if __name__ == "__main__":
    start_at = Chengjiaos.select().where(Chengjiaos.signed_at!=None).order_by(Chengjiaos.signed_at.asc()).limit(1)[0].signed_at.replace('.','-')
    end_at = Chengjiaos.select().order_by(Chengjiaos.signed_at.desc()).limit(1)[0].signed_at.replace('.','-')
    chengjiaos = Chengjiaos.select().order_by(Chengjiaos.signed_at)

    daily = {}
    for v in chengjiaos:
        if v.signed_at == None:
            continue
        v.signed_at = v.signed_at.replace('.','-')
        if v.signed_at not in daily.keys():
            daily[v.signed_at] = []
        daily[v.signed_at].append(v)

    current = datetime.datetime.now()
    date = current.strftime("%Y-%m-%d")

    while date >= start_at:
        print(date)
        if date > end_at:
            current = current - datetime.timedelta(days=1)
            date = current.strftime("%Y-%m-%d")
            continue
        try:
            stats = Stats.get(date = date, type = 'daily')
        except:
            stats = Stats()
            stats.date = date
            stats.type = 'daily'
        price = None
        unit_price = None
        signed_at = None
        period = None
        follows = None
        check = None
        view = None
        num = 0

        price_num = 0
        unit_price_num = 0
        period_num = 0
        follows_num = 0
        check_num = 0
        view_num = 0

        price_tatal = 0
        unit_price_tatal = 0
        period_tatal = 0
        follows_tatal = 0
        check_tatal = 0
        view_tatal = 0

        if date in daily.keys():
            for v in daily[date]:
                num = num + 1
                if v.price != None:
                    price_tatal = price_tatal + float(v.price)
                    price_num = price_num + 1
                if v.unit_price != None:
                    unit_price_tatal = unit_price_tatal + float(v.unit_price.replace('元/平', ''))
                    unit_price_num = unit_price_num + 1
                if v.period != None:
                    period_tatal = period_tatal + v.period
                    period_num = period_num + 1
                if v.follows != None:
                    follows_tatal = follows_tatal + v.follows
                    follows_num = follows_num + 1
                if v.check != None:
                    check_tatal = check_tatal + v.check
                    check_num = check_num + 1
                if v.view != None:
                    view_tatal = view_tatal + v.view
                    view_num = view_num + 1

        stats.price = None
        stats.unit_price = None
        stats.period = None
        stats.follows = None
        stats.check = None
        stats.view = None

        if price_tatal != 0:
            stats.price = price_tatal / price_num
        if unit_price_tatal != 0:
            stats.unit_price = unit_price_tatal / unit_price_num
        if period_tatal != 0:
            stats.period = period_tatal / period_num
        if follows_tatal != 0:
            stats.follows = follows_tatal / follows_num
        if check_tatal != 0:
            stats.check = check_tatal / check_num
        if view_tatal != 0:
            stats.view = view_tatal / view_num
        stats.signed_at = signed_at
        stats.num = num
        stats.save()
        current = current - datetime.timedelta(days=1)
        date = current.strftime("%Y-%m-%d")

    start_at = Chengjiaos.select().where(Chengjiaos.signed_at!=None).order_by(Chengjiaos.signed_at.asc()).limit(1)[0].signed_at.replace('.','-')
    end_at = Chengjiaos.select().order_by(Chengjiaos.signed_at.desc()).limit(1)[0].signed_at.replace('.','-')

    date = datetime.datetime.strptime(start_at, "%Y-%m-%d")
    day_cha = int(date.strftime("%w")) - 1
    if day_cha < 0:
        day_cha = 6
    date = date - datetime.timedelta(days=day_cha)
    start_at = date.strftime("%Y-%m-%d")

    date = datetime.datetime.strptime(end_at, "%Y-%m-%d")
    day_cha = int(date.strftime("%w")) - 1
    if day_cha < 0:
        day_cha = 6
    date = date - datetime.timedelta(days=day_cha)
    end_at = date.strftime("%Y-%m-%d")

    weekly = {}
    for v in chengjiaos:
        if v.signed_at == None:
            continue
        if len(v.signed_at) < 10:
            continue
        v.signed_at = v.signed_at.replace('.','-')
        date = datetime.datetime.strptime(v.signed_at, "%Y-%m-%d")

        day_cha = int(date.strftime("%w")) - 1
        if day_cha < 0:
            day_cha = 6
        date = date-datetime.timedelta(days=day_cha)
        date = date.strftime("%Y-%m-%d")
        if date not in weekly.keys():
            weekly[date] = []
        weekly[date].append(v)

    day_cha = int(datetime.datetime.now().strftime("%w")) - 1
    if day_cha < 0:
        day_cha = 6
    current = datetime.datetime.now() - datetime.timedelta(days=day_cha)

    date = current.strftime("%Y-%m-%d")

    while date >= start_at:
        if date > end_at:
            current = current - datetime.timedelta(days=1)
            date = current.strftime("%Y-%m-%d")
            continue
        try:
            stats = Stats.get(date = date, type = 'weekly')
        except:
            stats = Stats()
            stats.date = date
            stats.type = 'weekly'
        price = None
        unit_price = None
        signed_at = None
        period = None
        follows = None
        check = None
        view = None
        num = 0

        price_num = 0
        unit_price_num = 0
        period_num = 0
        follows_num = 0
        check_num = 0
        view_num = 0

        price_tatal = 0
        unit_price_tatal = 0
        period_tatal = 0
        follows_tatal = 0
        check_tatal = 0
        view_tatal = 0

        if date in weekly.keys():
            for v in weekly[date]:
                num = num + 1
                if v.price != None:
                    price_tatal = price_tatal + float(v.price)
                    price_num = price_num + 1
                if v.unit_price != None:
                    unit_price_tatal = unit_price_tatal + float(v.unit_price.replace('元/平', ''))
                    unit_price_num = unit_price_num + 1
                if v.period != None:
                    period_tatal = period_tatal + v.period
                    period_num = period_num + 1
                if v.follows != None:
                    follows_tatal = follows_tatal + v.follows
                    follows_num = follows_num + 1
                if v.check != None:
                    check_tatal = check_tatal + v.check
                    check_num = check_num + 1
                if v.view != None:
                    view_tatal = view_tatal + v.view
                    view_num = view_num + 1

        stats.price = None
        stats.unit_price = None
        stats.period = None
        stats.follows = None
        stats.check = None
        stats.view = None

        if price_tatal != 0:
            stats.price = price_tatal / price_num
        if unit_price_tatal != 0:
            stats.unit_price = unit_price_tatal / unit_price_num
        if period_tatal != 0:
            stats.period = period_tatal / period_num
        if follows_tatal != 0:
            stats.follows = follows_tatal / follows_num
        if check_tatal != 0:
            stats.check = check_tatal / check_num
        if view_tatal != 0:
            stats.view = view_tatal / view_num
        stats.signed_at = signed_at
        stats.num = num
        stats.save()
        current = current - datetime.timedelta(days=7)
        date = current.strftime("%Y-%m-%d")









