import requests
from bs4 import BeautifulSoup
from malls import Malls

if __name__ == "__main__":
    headers = {
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
        'Cookie': 'tt_webid=6634768059273332225; _ga=GA1.3.1307784653.1544777323; _gid=GA1.3.720099781.1544777323; _gat=1',
    }
    page = 1
    # while (page <=123):
    #     url = 'http://bizsearch.winshangdata.com/xiangmu/s0-c0-t2019-r0-g0-x0-d0-z0-n0-m0-l0-q0-b0-y0-pn' + str(page) + '.html'
    #     res = requests.get(url, headers=headers)
    #     print(page)
    #     page = page + 1
    #     soup = BeautifulSoup(res.content.decode('utf-8'), "html.parser")
    #     ul = soup.find("ul", class_="l-list")
    #     items = ul.find_all("li", class_="item")

    #     for item in items:
    #         # print(item)
    #         info = {
    #             'name': '',
    #             'link': '',
    #             'logo': '',
    #             'start_at': '',
    #             'area': '',
    #             'city': '',
    #             'address': '',
    #             'desc': '',
    #             'develop': '',
    #         }

    #         logo = item.attrs['data-pic']
    #         name = item.attrs['data-name']
    #         link = item.find('a').attrs['href']
    #         info['logo'] = logo
    #         info['name'] = name
    #         info['link'] = link
    #         try:
    #             mall = Malls.get(link=info['link'],name = name,logo = logo)
    #         except:
    #             mall = Malls()
    #         mall.name = name
    #         mall.logo = logo
    #         mall.link = link
    #         mall.save()

    malls = Malls.select().where(Malls.ranking_str == None)
    for mall in malls:
        info = {}
        res2 = requests.get(mall.link, headers=headers)
        print(res2.content.decode('utf-8').find('您所访问的页面没有找到，但不要着急哦！')>0)
        if res2.content.decode('utf-8').find('您所访问的页面没有找到，但不要着急哦！')>0:
            continue
        detail = BeautifulSoup(res2.content.decode('utf-8'), "html.parser")

        pid = detail.find(id='j-pid')['value']
        plink = 'http://www.winshangdata.com/bizhtm/html/hand/ppInfo.ashx'
        params = {
            'action': 'top',
            'type': '1',
            'id': str(pid),
        }
        rank_res = requests.get(plink, params=params, headers=headers)
        mall.ranking_str = rank_res.content.decode('utf-8')
        if rank_res.content.decode('utf-8') != '':
            content = rank_res.json()
            for d in content['ds']:
                mall.ranking = d['Titile'] + ' 第' + str(d['Ranking']) + '名'

        status = detail.find("ul", class_="d-inf-status")
        lis = status.find_all("li")
        for li in lis:
            spans = li.find_all("span")
            i = 1
            k = ''
            for span in spans:
                if i % 2 == 1:
                    k = span.get_text()
                    i = i + 1
                    continue
                i = i + 1
                if k == '所在城市':
                    info['city'] = span.get_text()
                if k == '开业时间':
                    info['start_at'] = span.get_text()
                if k == '项目地址':
                    info['address'] = span.get_text()
                if k == '商业建筑面积':
                    info['area'] = span.get_text()

        
        boxs = detail.find_all("div", class_="div-nav-cont")
        for box in boxs:
            h3 = box.find("h3")
            if h3 == None:
                continue
            if h3.get_text() == '项目简介':
                desc = box.find("div", class_="d-show")
                info['desc'] = desc.get_text()
                spans = box.find("ul").find("li").find_all("span")
                info['develop'] = spans[1].get_text()
        # print(info)
        mall.start_at = info['start_at']
        mall.area = info['area']
        mall.city = info['city']
        mall.address = info['address']
        mall.desc = info['desc']
        mall.develop = info['develop']
        mall.save()


