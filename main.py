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


def get_weather():
  url = "http://api.tianapi.com/tianqi/index?key= 8a1a8aabc5bce0999dc9fc57e0b31f80&city=" + city
  res1 = requests.get(url).json()
  muzi = res1['newslist'][0]
  #area 城市  week = 星期 weather = 今天天气  real = 当前温度  lowest = 最低气温  highest= 最高气温  wind = 风项  windsc = 风力 sunrise = 日出时间 sunset = 日落时间 pop = 降雨概率 tips = 穿衣建议 
  return muzi['area'], muzi['week'], muzi['weather'], muzi['real'], muzi['lowest'], muzi['highest'], muzi['wind'], muzi['windsc'], muzi['sunrise'], muzi['sunset'], muzi['tips']


def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
wea, temperature = get_weather()
data = {"weather":{"value":wea},"temperature":{"value":temperature},"love_days":{"value":get_count()},"birthday_left":{"value":get_birthday()},"words":{"value":get_words(), "color":get_random_color()}}
res = wm.send_template(user_id, template_id, data)
print(res)
