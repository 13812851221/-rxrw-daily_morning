from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
from requests.adapters import HTTPAdapter
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

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))

def get_weather():
  url = "https://restapi.amap.com/v3/weather/weatherInfo?key="+weather_key +"&city=130600"
  res = s.get(url,timeout=20)
  print('获取天气结果：',res)
  weather = res.json()['lives'][0]
  print('获取天气结果222：',weather)
  return weather['weather'], math.floor(int(weather['temperature']))



def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  print('start===文案开始时间：',datetime.now())
  words = s.get("https://api.shadiao.pro/chp",timeout=20)
  newwords = words.json()['data']['text']
  print('获取文案JSON：',newwords)
  return ""+newwords
  
  

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
