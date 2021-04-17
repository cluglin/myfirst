import time
from bs4 import BeautifulSoup
import json
import requests
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client['Rent_db']
collection = db['Rent_collection']


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
    for cookie in cookies:
        url = "https://rent.591.com.tw/home/search/rsList"
        for i in range(1):  # 設定爬多少物件(1=60個)
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
            time.sleep(1)
            data = json.loads(response.text)
            for i in data['data']['data']:
                if (i['shape'] == 0):  # house_type.append(i['shape'])  # 0沒有、1公寓、2電梯大樓、3透天厝、4別墅
                    house_type = ('No Value')
                elif (i['shape'] == 1):
                    house_type = ('公寓')
                elif (i['shape'] == 2):
                    house_type = ('電梯大樓')
                elif (i['shape'] == 3):
                    house_type = ('透天厝')
                elif (i['shape'] == 4):
                    house_type = ('別墅')
                if ('girl' in i['condition']):
                    sex_req = ('限女性')
                elif ('boy' in i['condition']):
                    sex_req = ('限男性')
                elif ('all_sex' in i['condition']):
                    sex_req = ('男女性皆可')
                if cookie == {"urlJumpIp": "1"}:
                    region = "台北"
                else:
                    region = "新北"
                collection.insert_one({
                    "網址": 'https://rent.591.com.tw/rent-detail-' + str(i['id']) + '.html',
                    "地區": region,
                    "出租者": i['linkman'],
                    "出租者身份": i['nick_name'].split(' ')[0],
                    "型態": house_type,
                    "現況": i['kind_name'],
                    "性別要求": sex_req
                })
if __name__=="__main__":
    session = requests.session()
    headers = Get_Headers(session)
    Get_Info(session, headers)
