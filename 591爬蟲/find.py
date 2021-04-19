from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client['Rent_db']
col = db['Rent_collection']

col.remove({'電話': None})
for i in col.find({'電話': None}):
    print(i['url'])
print('共', col.find().count(), '筆資料')
print('共', col.find({}, {'電話': 1}).count(), '筆電話資料')
print(col.find({'電話': None}).count(), '筆沒有電話資料')
