import re
from flask import Flask,request,jsonify
from pymongo import MongoClient
import json
def Connect_to_Database():
    client = MongoClient('localhost', 27017)
    db = client['Rent_db']
    col = db['Rent_collection']
    return col
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False 
@app.route('/')
def hello_world():
    return 'Hello, World!'
 
@app.route('/search',methods=['GET'])
def getQ(): 
    condition,condition2 = Get_condition()
    data = Get_data(condition,condition2)
    return data

def Get_condition ():
    condition = {}
    condition2 = {}
    region_map = {'1':'台北','2':'新北'}
    renter_title_map = {'1':'屋主','2':'仲介','3':'代理人'}
    list = ['region','sex_req','phone','renter_title','renter_is_woman','last_name']
    for i in list:
        value = request.args.get(i)
        if value is not None:
            if i == 'region':
                condition[i] = region_map.get(value)
            elif i == 'sex_req':
                if value == '1':
                    condition[i] = {'$nin':['限女性']}
                if value == '2':
                    condition[i] = {'$nin':['限男性']}
            elif i == 'renter_title':
                for key in renter_title_map.keys():
                    value = value.replace(key,renter_title_map[key])
                condition[i] = {'$in':value.split(',')}
            elif (i == 'renter_is_woman') & (value == '1'):
                condition['renter'] ={'$regex':'太太|媽媽|阿姨|小姐|女士'}
            elif i == 'last_name':
                last_name = '^{name}'.format(name=value)
                condition2['renter'] = {'$regex':last_name} 
            elif i =='phone':
                condition['phone'] ={'$regex':value}
    return condition,condition2

def Get_data(condition,condition2):

    result = col.find({'$and':[condition,condition2]},{'_id':0})
    data_json = {
        'amount':result.count(),
        'data': list(result)
    }
    return data_json

if __name__ == '__main__':
    col = Connect_to_Database()
    app.run(debug=True, host='0.0.0.0', port=8001)

