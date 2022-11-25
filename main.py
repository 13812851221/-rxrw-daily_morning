from datetime import datetime, timedelta
from requests import Response
from wechatpy import WeChatClient, WeChatClientException
from wechatpy.client.api import WeChatMessage
from borax.calendars.lunardate import LunarDate
import math
import requests
import os
import re
import random
import xmltodict

nowtime = datetime.utcnow() + timedelta(hours=8)  # 东八区时间
today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d")  # 今天的日期
today1 = LunarDate.today()

city = os.getenv('CITY')
start_date = os.getenv('START_DATE')
birthday = os.getenv('BIRTHDAY')

app_id = os.getenv('APP_ID')
app_secret = os.getenv('APP_SECRET')

user_ids = os.getenv('USER_ID', '').split("\n")
url = "https://lab.magiconch.com/sakana/?v=takina"
template_id = os.getenv('TEMPLATE_ID')

# 为读取农历生日准备
lubaryear1 = today1.year
x = int(birthday[0:4:1])  # 读取无用，为理解下面两行留着，可删去
y = int(birthday[5:7])  # 切片
z = int(birthday[8:10])
birthday1 = LunarDate(lubaryear1, y, z)  # 构建今年农历生日日期
birthday2 = birthday1.to_solar_date()  # 转化成公历日期，输出为字符串

# 为读取星座准备
xingzuo1 = LunarDate(x, y, z)  # 构建农历生日日期
xingzuo2 = xingzuo1.to_solar_date()
cmonth = int(xingzuo2.strftime('%Y-%m-%d')[5:7])  # 切片
cdate = int(xingzuo2.strftime('%Y-%m-%d')[8:])
sdate = [20, 19, 21, 20, 21, 22, 23, 23, 23, 24, 23, 22]
conts = ['摩羯座', '水瓶座', '双鱼座', '白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座', '天秤座', '天蝎座',
         '射手座', '摩羯座']


def sign(cmonth, cdate):
    if int(cdate) < sdate[int(cmonth) - 1]:  # 如果日数据早于对应月列表中对应的日期
        return conts[int(cmonth) - 1]  # 直接输出星座列表对应月对应的星座
    else:
        return conts[int(cmonth)]


if app_id is None or app_secret is None:
    print('请设置 APP_ID 和 APP_SECRET')
    exit(422)

if not user_ids:
    print('请设置 USER_ID，若存在多个 ID 用空格分开')
    exit(422)

if template_id is None:
    print('请设置 TEMPLATE_ID1')
    exit(422)


# if template_id2 is None:
# print('请设置 TEMPLATE_ID2')
# exit(422)

# weather 直接返回对象，在使用的地方用字段进行调用。
def get_weather_3():
    url = "http://www.tianqiapi.com/api?version=v1&appid=78158848&appsecret=650ylFRx&city=" + city
    res3 = requests.get(url)
    if res3.status_code != 200:
        return res3
    #res31 = xmltodict.parse(res3.text)['resp']
    res31 = res3.json()['data']
    res311 = res31[0]['index']
    return res31[1]['wea'],res31[2]['wea'],res31[3]['wea'],res31[4]['wea'],res31[5]['wea'],res31[6]['wea'],res311[0]['desc'],res311[1]['desc'],res311[2]['desc'],res311[3]['desc'],res311[4]['desc'],res311[5]['desc'],res31[0]['week'], res31[0]['sunrise'], res31[0]['sunset'], res31[0]['wea'],res31[0]['humidity'],res31[0]['alarm'], res31[0]['air_level'], res31[0]['win'], res31[0]['win_speed'], res31[0]['tem'], res31[0]['tem2'], res31[0]['tem1']


# 星座
def get_xingzuo():
    url = "http://api.tianapi.com/star/index?key=d5edced4967c76fd11899dbe1b753d91&astro=" + sign(cmonth, cdate)
    xingzuo = requests.get(url, verify=False)
    if xingzuo.status_code != 200:
        return xingzuo
    data = xingzuo.json()['newslist']
    return data[5]["content"], data[3]["content"], data[6]["content"], data[1]["content"], data[2]["content"], data[4][
        "content"], data[7]["content"], data[8]["content"]


# 疫情接口
def get_Covid_19():
    url = "https://covid.myquark.cn/quark/covid/data?city=" + city
    res3 = requests.get(url)
    if res3.status_code != 200:
        return res3
    if city in ["北京", "上海", "天津", "重庆", "香港", "澳门", "台湾"]:
        res31 = res3.json()["provinceData"]
    else:
        res31 = res3.json()["cityData"]
    return res31["sure_new_loc"], res31["sure_new_hid"], res31["present"], res31["danger"]["1"], res31["danger"]["2"]


# 农历接口
def get_lunar_calendar():
    date = today.strftime("%Y-%m-%d")
    url = "http://api.tianapi.com/lunar/index?key=d5edced4967c76fd11899dbe1b753d91&date=" + date
    lunar_calendar = requests.get(url, verify=False)
    if lunar_calendar.status_code != 200:
        return get_lunar_calendar()
    res3 = lunar_calendar.json()['newslist'][0]
    return res3['lubarmonth'], res3['lunarday'], res3['jieqi'], res3['lunar_festival'], res3['festival']


# 纪念日正数
def get_memorial_days_count():
    if start_date is None:
        print('没有设置 START_DATE')
        return 0
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days


# 生日倒计时
def get_counter_left(aim_date):
    if aim_date is None:
        return 0

    y = int(aim_date[5:7])  # 切片
    z = int(aim_date[8:10])
    birthday1 = LunarDate(lubaryear1, y, z)  # 构建今年农历生日日期
    birthday2 = birthday1.to_solar_date()
    next = datetime.strptime(birthday2.strftime("%Y-%m-%d"), "%Y-%m-%d")

    if next < nowtime:
        birthday11 = LunarDate(lubaryear1 + 1, y, z)
        birthday21 = birthday11.to_solar_date()
        next = datetime.strptime(birthday21.strftime("%Y-%m-%d"), "%Y-%m-%d")
    return (next - today).days


def split_birthday():
    if birthday is None:
        return None
    return birthday.split('\n')


# 元旦节倒计时
def get_yuandan():
    yuandan = datetime.strptime(str(today.year) + "-" + "01" + "-" + "01", "%Y-%m-%d")  # 元旦
    next1 = (datetime.strptime(yuandan.strftime("%Y-%m-%d"), "%Y-%m-%d") - today).days
    if next1 < 0 or next1 > 15:
        return None
    elif next1 > 0 and next1 <= 15:
        next1 = "距离元旦还有" + str(next1) + "天"
    else:
        next1 = "元旦快乐！！！"
    return next1


# 春节倒计时
def get_chunjie():
    spring_festival = LunarDate(lubaryear1, 1, 1).to_solar_date()
    next2 = (datetime.strptime(spring_festival.strftime("%Y-%m-%d"), "%Y-%m-%d") - today).days
    if next2 < 0 or next2 > 15:
        return None
    elif next2 > 0 and next2 <= 15:
        next2 = "距离大年初一还有" + str(next2) + "天"
    else:
        next2 = "过年好！恭喜发财"
    return next2


# 踏青节倒计时
def get_taqing():
    sching_ming_festival = LunarDate(lubaryear1, 3, 5).to_solar_date()
    next3 = (datetime.strptime(sching_ming_festival.strftime("%Y-%m-%d"), "%Y-%m-%d") - today).days
    if next3 < 0 or next3 > 0:
        return None
    else:
        next3 = "况是清明好天气，不妨游衍莫忘归"
    return next3


# 劳动节倒计时
def get_laodong():
    laodong = datetime.strptime(str(today.year) + "-" + "05" + "-" + "01", "%Y-%m-%d")
    next4 = (datetime.strptime(laodong.strftime("%Y-%m-%d"), "%Y-%m-%d") - today).days
    if next4 < 0 or next4 > 15:
        return None
    elif next4 > 0 and next4 <= 15:
        next4 = "距离劳动节还有" + str(next4) + "天"
    else:
        next4 = "三天休息日"
    return next4


# 端午节倒计时
def get_duanwu():
    duanwu = LunarDate(lubaryear1, 5, 5).to_solar_date()
    next5 = (datetime.strptime(duanwu.strftime("%Y-%m-%d"), "%Y-%m-%d") - today).days
    if next5 < 0 or next5 > 15:
        return None
    elif next5 > 0 and next5 <= 15:
        next5 = "距离端午节还有" + str(next5) + "天"
    else:
        next5 = "今日宜划龙舟，吃粽子"
    return next5


# 中秋节倒计时
def get_zhongqiu():
    mid_autumn_festival = LunarDate(lubaryear1, 8, 15).to_solar_date()
    next6 = (datetime.strptime(mid_autumn_festival.strftime("%Y-%m-%d"), "%Y-%m-%d") - today).days
    if next6 < 0:
        return None
    elif next6 > 0 and next6 <= 15:
        next6 = "距离中秋节还有" + str(next6) + "天"
    else:
        next6 = "春江潮水连海平，莲蓉豆沙冰淇淋"
    return next6


# 国庆节节倒计时
def get_guoqing():
    guoqing = datetime.strptime(str(today.year) + "-" + "10" + "-" + "01", "%Y-%m-%d")
    next7 = (datetime.strptime(guoqing.strftime("%Y-%m-%d"), "%Y-%m-%d") - today).days
    if next7 < 0 or next7 > 15:
        return None
    elif next7 > 0 and next7 <= 15:
        next7 = "距离国庆节还有" + str(next7) + "天"
    else:
        next7 = "生在红旗下，长在春风里"
    return next7


# 彩虹屁 接口不稳定，所以失败的话会重新调用，直到成功
def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    return words.json()['data']['text']


def format_temperature(temperature):
    return math.floor(temperature)


# 随机颜色
def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


try:
    client = WeChatClient(app_id, app_secret)
except WeChatClientException as e:
    print('微信获取 token 失败，请检查 APP_ID 和 APP_SECRET，或当日调用量是否已达到微信限制。')
    exit(502)

wm = WeChatMessage(client)
Day_1, Day_2, Day_3, Day_4, Day_5, Day_6, Ultraviolet, jianfei, xuetang, dressing, xiche, air_pollution,week, sunrise, sunset, weather,humidity,alarm1, aqi, win, win_speed, tem, tem1, tem2 = get_weather_3()
lubarmonth, lunarday, jieqi, lunar_festival, festival = get_lunar_calendar()
lucky, finances, shuzi, aiqing, gongzuo, jiankang, guiren, gaishu = get_xingzuo()
sure_new_loc, sure_new_hid, present, danger1, danger2 = get_Covid_19()
jieri = get_yuandan(), get_chunjie(), get_taqing(), get_laodong(), get_duanwu(), get_zhongqiu(), get_guoqing()
jieri2 = ''.join(list(filter(None, jieri)))
alarm2 = alarm1.get('alarm_level')


def get_weather_icon(weather):
    weather_icon = "🌈"
    weather_icon_list = ["☀️", "☁️", "⛅️",
                         "☃️", "⛈️", "🏜️", "🏜️", "🌫️", "🌫️", "🌪️", "🌧️"]
    weather_type = ["晴", "阴", "云", "雪", "雷", "沙", "尘", "雾", "霾", "风", "雨"]
    for index, item in enumerate(weather_type):
        if re.search(item, weather):
            weather_icon = weather_icon_list[index]
            break
    return weather_icon

data = {
    "1": {
        "value": today.strftime('%Y年%m月%d日') + week,
        "color": get_random_color()
    },
    "2": {
        "value": lubarmonth + lunarday + jieqi + lunar_festival + festival + jieri2,
        "color": get_random_color()
    },
    "3": {
        "value": get_weather_icon(weather) + weather,
        "color": get_random_color()
    },
    "4": {
        "value": city,
        "color": get_random_color()
    },
    "5": {
        "value": tem + "℃",
        "color": get_random_color()
    },
    "6": {
        "value": Day_1 + "~" + Day_2 + "~" + Day_3 + "~" + Day_4 + "~" + Day_5+ "~" + Day_6,
        "color": get_random_color()
    },
    "7": {
        "value": tem1 + "℃" + "~" + tem2 + "℃",
        "color": get_random_color()
    },
    "8": {
        "value": sunrise,
        "color": get_random_color()
    },
    "9": {
        "value": sunset,
        "color": get_random_color()
    },
    "a": {
        "value": win[0],
        "color": get_random_color()
    },
    "b": {
        "value": humidity,
        "color": get_random_color()
    },
    "c": {
        "value": aqi,
        "color": get_random_color()
    },
    "d": {
        "value": shuzi,
        "color": get_random_color()
    },
    "e": {
        "value": finances,
        "color": get_random_color()
    },
    "f": {
        "value": lucky,
        "color": get_random_color()
    },
    "g": {
        "value": sure_new_loc,
        "color": get_random_color()
    },
    "h": {
        "value": sure_new_hid,
        "color": get_random_color()
    },
    "i": {
        "value": present,
        "color": get_random_color()
    },
    "j": {
        "value": str(danger1) + "/" + str(danger2),
        "color": get_random_color()
    },
    "k": {
        "value": dressing,
        "color": get_random_color()
    },
    "l": {
        "value": get_memorial_days_count(),
        "color": get_random_color()
    },
    "n": {
        "value": alarm2,
        "color": "#FF0000",
    },
    "o": {
        "value": Ultraviolet,
        "color": get_random_color()
    },
    "p": {
        "value": jianfei,
        "color": get_random_color()
    },
    "q": {
        "value": get_words(),
        "color": get_random_color()
    },
    "r": {
        "value": xuetang,
        "color": get_random_color()
    },
    "s": {
        "value": xiche,
        "color": get_random_color()
    },
    "t": {
        "value": air_pollution,
        "color": get_random_color()
    },
    "z": {
        "value": aiqing,
        "color": get_random_color()
    },
    "A": {
        "value": gongzuo,
        "color": get_random_color()
    },
    "B": {
        "value": jiankang,
        "color": get_random_color()
    },
    "C": {
        "value": guiren,
        "color": get_random_color()
    },
    "D": {
        "value": gaishu,
        "color": get_random_color()
    },
}

for index, aim_date in enumerate(split_birthday()):
    key_name = "m"
    if index != 0:
        key_name = key_name + "_%d" % index
    data[key_name] = {
        "value": get_counter_left(aim_date),
        "color": get_random_color()
    }

if __name__ == '__main__':
    count = 0
    try:
        for user_id in user_ids:
            res = wm.send_template(user_id, template_id, data, url)
            count += 1
    except WeChatClientException as e:
        print('微信端返回错误：%s。错误代码：%d' % (e.errmsg, e.errcode))
        exit(502)

    print("发送了" + str(count) + "条消息")
