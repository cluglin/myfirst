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

def Get_amount():
    amount = []
    url = ['1','3']
    for i in range(2):
        with requests.session() as s:
            session = s.get('https://rent.591.com.tw/?kind=0&region=3', cookies={"urlJumpIp":url[i]})
            soup = BeautifulSoup(session.text, 'html.parser')
            amount.append(int(soup.find('div',{'class':'pull-left hasData'}).find('i').text[1:-1].replace(',','')))
    return amount

def Get_Info(session, headers, amount):  # 從這個api抓物件(網址、出租者、出租者身分、型態、現況、性別要求)
    cookies = [{"urlJumpIp": "1"}, {"urlJumpIp": "3"}]  # 1=台北，3=新北
    house_type_map = {0: "No Value", 1: "公寓", 2: "電梯大樓",
                      3: "透天厝", 4: "別墅", 5: "華廈", 6: "住宅大樓", 8: "店面(店鋪)"}
    count = 0
    no_count = 0
    for two in range(2):
        times = int(amount[two]/30)
        for x in range(times):
            url = "https://rent.591.com.tw/home/search/rsList"
            params = {
                "is_new_list": 1,
                "type": 1,
                "kind": 0,
                "searchtype": 1,
                "region": 1,
                "firstRow":30*(x+1),
                "totalRows": amount[two]
            }
            response = session.get(
                url, params=params, headers=headers, cookies=cookies[two])
            data = json.loads(response.text)
            for i in data['data']['data']:
                if col.find({'url':'https://rent.591.com.tw/rent-detail-' + str(i['id']) + '.html'}).count() ==0: #資料庫沒有重複物件
                    count+=1
                    print(count)
                    house_type = house_type_map.get(i['shape'])
                    if ('girl' in i['condition']):
                        sex_req = ('限女性')
                    elif ('boy' in i['condition']):
                        sex_req = ('限男性')
                    else:
                        sex_req = ('男女性皆可')
                    if cookies[two] == {"urlJumpIp": "1"}:
                        region = "台北"
                    else:
                        region = "新北"
                    col.insert_one({
                        "url": 'https://rent.591.com.tw/rent-detail-' + str(i['id']) + '.html',
                        "region": region,
                        "renter": i['linkman'],
                        "renter_title": i['nick_name'].split(' ')[0],
                        "house_type": house_type,
                        "situation": i['kind_name'],
                        "sex_req": sex_req
                    })
                else:
                    no_count+=1
                    continue
    print('新增',count,'筆資料','略過',no_count,'筆資料')

def Get_phone():
    count = 0
    no_count = 0
    for i in col.find({'phone':None}):
        url = i['url']
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        if soup.find('span', 'dialPhoneNum') == None: #若物件已銷售會出現找不到電話的狀況
            no_count+=1
            continue
        else:
            phone = soup.find('span', 'dialPhoneNum').get('data-value')
            if phone == '':
                phone = soup.find('div', 'hidtel').text
            col.update({'url':url},{'$set':{'phone':phone}})
            print(phone)
            count+=1
    print('新增',count,'筆電話資料','略過',no_count,'筆電話資料')

def Delete_Selled_Obj(col):
    print('下為無電話資料的物件資料')
    for i in col.find({'phone':None}):
        print(i)
    print('刪除',col.find({'phone':None}).count(),'筆無電話的資料')
    col.remove({'phone':None})

if __name__=='__main__':
    session = requests.session()
    headers = Get_Headers(session)
    amount = Get_amount()
    Get_Info(session, headers, amount)
    Get_phone()
    if col.find({'phone':None}).count() != 0:
        Delete_Selled_Obj(col)
