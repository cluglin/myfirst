import time
from bs4 import BeautifulSoup
import json
import requests
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client['Rent_db']
col = db['Rent_collection']


# api https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=0&searchtype=1&region=1&firstRow=30&totalRows=12242
# region只是幌子，改了也不會變更地區，要改地區請找urlJumpIp

# 為了取得CSRF、還有重設瀏覽器cookies預設的urlJumpIp，所以需要先發一個session，CSRF是為了套用API 需要夾在headers裡
def Get_Headers(session):
    session = session.get(
        'https://rent.591.com.tw/?kind=0&region=3', cookies={"urlJumpIp": "5"})
    soup = BeautifulSoup(session.text, 'html.parser')
    csrf = soup.find('meta', {'name': 'csrf-token'}).get('content')
    headers = {
        "X-CSRF-TOKEN": csrf,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36"
    }
    return headers


def Get_Info(session, headers):  # 從這個api抓物件(網址、出租者、出租者身分、型態、現況、性別要求)
    cookies = [{"urlJumpIp": "1"}, {"urlJumpIp": "3"}]  # 1=台北，3=新北
    house_type_map = {0: "No Value", 1: "公寓", 2: "電梯大樓",
                      3: "透天厝", 4: "別墅", 5: "華廈", 6: "住宅大樓", 8: "店面(店鋪)"}
    count = 0
    no_count = 0
    for cookie in cookies:
        url = "https://rent.591.com.tw/home/search/rsList"
        for i in range(297):  # 設定爬多少物件(1=60個)
            params = {
                "is_new_list": 1,
                "type": 1,
                "kind": 0,
                "searchtype": 1,
                "region": 1,
                "firstRow": i*30,
                "totalRows": 21000
            }
            response = session.get(
                url, params=params, headers=headers, cookies=cookie)
            data = json.loads(response.text)
            for i in data['data']['data']:
                # 資料庫沒有這個物件
                if col.find({'url': 'https://rent.591.com.tw/rent-detail-' + str(i['id']) + '.html'}).count() == 0:
                    count += 1
                    print(count)
                    house_type = house_type_map.get(i['shape'])
                    if ('girl' in i['condition']):
                        sex_req = ('限女性')
                    elif ('boy' in i['condition']):
                        sex_req = ('限男性')
                    else:
                        sex_req = ('男女性皆可')
                    if cookie == {"urlJumpIp": "1"}:
                        region = "台北"
                    else:
                        region = "新北"
                    col.insert_one({
                        "url": 'https://rent.591.com.tw/rent-detail-' + str(i['id']) + '.html',
                        "地區": region,
                        "出租者": i['linkman'],
                        "出租者身份": i['nick_name'].split(' ')[0],
                        "型態": house_type,
                        "現況": i['kind_name'],
                        "性別要求": sex_req
                    })
                else:
                    no_count += 1
                    continue
    print('新增', count, '筆資料', '略過', no_count, '筆資料')


def Get_phone():
    count = 0
    no_count = 0
    for i in col.find({'電話': None}):
        url = i['url']
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        if soup.find('span', 'dialPhoneNum') == None:
            no_count += 1
            continue
        else:
            phone = soup.find('span', 'dialPhoneNum').get('data-value')
            if phone == '':
                phone = soup.find('div', 'hidtel').text
            col.update({'url': url}, {'$set': {'電話': phone}})
            print(phone)
            count += 1
    print('新增', count, '筆電話資料', '略過', no_count, '筆電話資料')


if __name__ == '__main__':
    session = requests.session()
    headers = Get_Headers(session)
    Get_Info(session, headers)
    Get_phone()
