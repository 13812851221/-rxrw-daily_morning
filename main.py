from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]

weather_key = os.environ["WEATHER_KEY"]

def get_weather():
  url = "https://restapi.amap.com/v3/weather/weatherInfo?key=21dac7a0611332385badf4b96449582c&city=130600"
  try:
    print('获取天气url：',url)
    print('start===天气开始时间：',datetime.now())
    res = requests.get(url,timeout=20)
    print('获取天气结果：',res.json()['lives'][0])
    weather = res.json['lives'][0]
    return weather['weather'], math.floor(int(weather['temperature']))
  except:
    print('end===天气结束时间：',datetime.now())
    print('获取天气出现异常')
    return '如往常','比较正常'


def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  try:
    print('start===文案开始时间：',datetime.now())
    words = requests.get("https://api.shadiao.pro/chp",timeout=20)
    print('获取文案JSON：',words.json())
    return words.json()['data']['text']
  except:
    print('end===文案结束时间：',datetime.now())
    print('获取文案出现异常')
    return '一想到你，我这张脸就泛起微笑——梁育德TO陈明'
  
  

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
wea, temperature = get_weather()
data = {"city":{"value":city, "color":get_random_color()},
        "weather":{"value":wea, "color":get_random_color()},
        "temperature":{"value":temperature, "color":get_random_color()},
        "love_days":{"value":get_count(), "color":get_random_color()},
        "birthday_left":{"value":get_birthday(), "color":get_random_color()},
        "words":{"value":get_words(), "color":get_random_color()}}
res = wm.send_template(user_id, template_id, data)
print(res)
