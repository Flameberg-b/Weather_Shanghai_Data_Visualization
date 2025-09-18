import requests
import os
from lxml import etree
import csv


def getWeather(url):
    weatherInfo = []
        # set useragent for requests
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1'
    }
    
    #请求
    resp = requests.get(url, headers=headers)
    #数据预处理
    respHtml = etree.HTML(resp.text)
    #Xpath提取所有数据
    respList = respHtml.xpath('//ul[@class="thrui"]/li')

    for li in respList:
        #将每日数据存入一个字典
        dayWeatherInfo = {}
        #日期
        dayWeatherInfo['date'] = li.xpath('./div[1]/text()')[0].split(' ')[0]
        #最高最低气温
        high = li.xpath('./div[2]/text()')[0]
        low = li.xpath('./div[3]/text()')[0]
        dayWeatherInfo['high'] = high[:high.find('℃')]
        dayWeatherInfo['low'] = low[:low.find('℃')]
        #天气
        dayWeatherInfo['weather'] = li.xpath('./div[4]/text()')[0]
        weatherInfo.append(dayWeatherInfo)

    return weatherInfo

weathers = []

for month in range(1, 13):
    weatherTime = '2024' + (str(month) if month > 9 else '0' + str(month))
    url = f'https://lishi.tianqi.com/shanghai/{weatherTime}.html'
    weather = getWeather(url)
    weathers.append(weather)

print(weathers)


#将每月数据存入总数据
with open('weather.csv', "w" ,newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    #写入头部
    writer.writerow(['date', 'high', 'low', 'weather'])
    #写入数据
    writer.writerows(list(dayWeatherDict.values()) for monthWeather in weathers for dayWeatherDict in monthWeather)
    
