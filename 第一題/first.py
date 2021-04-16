import xml.etree.ElementTree as ET
import pandas as pd
urls = ['./lvr_landxml/a_lvr_land_a.xml',
        './lvr_landxml/b_lvr_land_a.xml',
        './lvr_landxml/e_lvr_land_a.xml',
        './lvr_landxml/f_lvr_land_a.xml',
        './lvr_landxml/h_lvr_land_a.xml']


def Create_DataFrame(url):
    data = []
    cols = []
    xml = open(url, 'r').read()
    root = ET.XML(xml)  # 解析XML為節點
    for child in root:
        # 用剝洋蔥的方式將tag裡面的內容存到data
        data.append([subchild.text for subchild in child])
    cols.append([subchild.tag for subchild in child])  # 欄位名稱=tag
    df = pd.DataFrame(data)
    df.columns = cols[0]
    return df


def Create_df_all():  # 合併五個DataFrame
    df_a = Create_DataFrame(urls[0])
    df_b = Create_DataFrame(urls[1])
    df_e = Create_DataFrame(urls[2])
    df_f = Create_DataFrame(urls[3])
    df_h = Create_DataFrame(urls[4])
    df_all = pd.concat([df_a, df_b, df_e, df_f, df_h])
    return df_all


def Create_filter_a(df_all):  # filter_a.csv的篩選條件
    build_floor = ['一層', '二層', '三層', '四層', '五層', '六層',
                   '七層', '八層', '九層', '十層', '十一層', '十二層']
    filter_1 = (df_all['主要用途'] == '住家用')
    filter_2 = (df_all['建物型態'].str.contains('住宅大樓'))
    filter_3 = (df_all['總樓層數'].notnull() & ~(df_all['總樓層數'].isin(build_floor)))
    filter_all = filter_1 & filter_2 & filter_3
    return filter_all


def Create_filter_a_csv(dataframe, filter):  # 輸出 filter_a.csv
    df_SAMPLE = pd.DataFrame.from_dict(
        dataframe[filter])
    df_SAMPLE.to_csv('filter_a.csv', index=False)
    print('輸出filter_a.csv成功')


def Create_filter_b_csv(df_all):
    amount = len(df_all)  # 總件數

    car = []
    for i in df_all['交易筆棟數']:
        car.append(int(i.split('車位')[1]))
    sum_car = sum(car)  # 總車位數

    all_money = []
    for i in df_all['總價元']:
        all_money.append(int(i))
    avg_money = sum(all_money)/amount  # 平均總價元

    all_car_money = []
    for i in df_all['車位總價元']:
        all_car_money.append(int(i))
    avg_car_money = sum(all_car_money) / sum_car  # 平均車位總價元

    ser1 = pd.Series(['總件數', '總車位數', '平均總價元', '平均車位總價元'])
    ser2 = pd.Series([amount, sum_car, avg_money, avg_car_money])
    # 建立filter_b的DataFrame
    df_filter_b_csv = pd.DataFrame({'第一欄': ser1, '第二欄': ser2})
    df_filter_b_csv.to_csv('filter_b.csv', index=False)
    print('輸出filter_b.csv成功')


if __name__ == '__main__':
    df_all = Create_df_all()
    filter_all = Create_filter_a(df_all)
    Create_filter_a_csv(df_all, filter_all)
    Create_filter_b_csv(df_all)
