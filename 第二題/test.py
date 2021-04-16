import requests
import json
from bs4 import BeautifulSoup
import time
# 台北市 前30 https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=0&searchtype=1&region=1
# 台北市 後30 https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=0&searchtype=1&region=1&firstRow=20&totalRows=12242
# 新北市 後30 https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=0&searchtype=1&region=3&firstRow=20&totalRows=9025
#             https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=0&searchtype=1&region=3


def Get_Headers(session):
    session = session.get(
        'https://rent.591.com.tw/?kind=0&region=3', cookies={"urlJumpIp": "5"})
    soup = BeautifulSoup(session.text, 'html.parser')
    csfr = soup.find('meta', {'name': 'csrf-token'}).get('content')
    headers = {
        "X-CSRF-TOKEN": csfr,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36"
    }
    return headers


def Get_House_Url(session, headers):
    house_url = []
    cookies = [{"urlJumpIp": "1"}, {"urlJumpIp": "3"}]  # 1=台北，3=新北
    for cookie in cookies:
        url = "https://rent.591.com.tw/home/search/rsList"
        params = {
            "is_new_list": 1,
            "type": 1,
            "kind": 0,
            "searchtype": 1,
            "region": 1
        }
        response = session.get(
            url, params=params, headers=headers, cookies=cookie)
        data = json.loads(response.text)
        for i in data['data']['topData']:
            house_url.append('https://rent.591.com.tw/'+i['detail_url'])
        print(len(house_url))
        # ============================上面為前20筆，下面為20筆後，每次抓新的20筆==========================================
        for i in range(1):
            params = {
                "is_new_list": 1,
                "type": 1,
                "kind": 0,
                "searchtype": 1,
                "region": 1,
                "firstRow": (i+1)*20,
                "totalRows": 21000
            }
            response = session.get(
                url, params=params, headers=headers, cookies=cookie)
            time.sleep(1)
            data = json.loads(response.text)
            for i in data['data']['topData']:
                house_url.append('https://rent.591.com.tw/'+i['detail_url'])
            print(len(house_url))
    return house_url


session = requests.session()
headers = Get_Headers(session)
house_url = Get_House_Url(session, headers)  # 物件的資訊頁面
print(house_url[70])
