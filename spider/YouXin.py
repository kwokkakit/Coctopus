#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import ConfigParser
import re
import os

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import common
import db
import spider


# TODO: 增加每日新增车辆的统计
# TODO: 增加日志的输出
# TODO: 优化车标题的存储，按品牌、型号、拆分数据入库
# TODO: 增加车辆如果是付一半，理财产品的抓取，可以得到总车价
# TODO; 修复判断车辆已卖出后的BUG


class YouXin(spider.Spider):
    def __init__(self, db_conf, phantomjs):
        # 使用PhantomJS获取渲染后页面
        self.PHANTOMJS_PATH = phantomjs
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.2372.400 QQBrowser/9.5.10548.400")
        self.driver = webdriver.PhantomJS(executable_path=self.PHANTOMJS_PATH, desired_capabilities=dcap)

        # 初始化数据库连接
        self.conn = db.DBHandler(
            {'host': db_conf.get('hostname'), 'port': int(db_conf.get('port')), 'user': db_conf.get('username'),
             'passwd': db_conf.get('passwd'), 'db': db_conf.get('database'), 'charset': db_conf.get('charset')})

        # 初始化基础工具
        self.tools = common.Tools()

        # 初始化公共变量
        self.BASE_URL = "http://www.xin.com"

        # 抓取方式
        # FLAG = 1: 城市抓取
        # FLAG = 2: 城市+品牌抓取
        # FLAG = 3: 城市+品牌+型号抓取
        self.FLAG = 3

    def getCity(self, url):
        city_url_list = []
        try:
            driver = self.driver
            driver.get(url)

            # 提取页面中的城市
            city_soup = BeautifulSoup(driver.page_source, "lxml")
            city_content = city_soup.find_all("div", class_='ci_m_city ci_m_list')
            cities = re.findall("<a\s*cityid=\"(.*?)\"\shref=['\"](.*?)['\"]>(.*?)</a>*", str(city_content))

            # location_id = re.findall("cityid=\"\d*\"\shref", str(city_content))
            # location_url = re.findall("<a\scityid=\"\d*\"\shref=\"/(.*?)/\">*", str(city_content))
            # location_city = re.findall("<a\s*cityid\s*=\s*\"[0-9]*\"\shref=['\"]/\w*/['\"]>(.*?)</a>*",
            #                            str(city_content))

            for city_link in cities:
                city_id = city_link[0]
                city_url = city_link[1]
                city_name = city_link[2]

                # 组装城市URL列表
                city_url_list.append(city_url)

                # 组装城市记录入库
                tablename = 'cityinfo'
                data = dict()
                data.update(city_id=city_id)
                result = self.conn.isInRecord(tablename, data)
                if result:
                    continue
                else:
                    data.update(city_id=city_id, city_name=city_name.decode('unicode-escape'),
                                city_url=city_url)
                    self.conn.insert(tablename, data)

            return city_url_list
        except Exception as e:
            print "Location" + str(e)

    def getBrand(self, url):
        brand_url_list = []
        try:
            # driver = self.driver
            # driver.get(index_page)
            # brand_soup = BeautifulSoup(driver.page_source, "lxml")
            brand_soup = BeautifulSoup(requests.get(url).content, "html.parser")
            brand_content = brand_soup.find_all("a", class_=" preventdefault")
            brands = re.findall("<a.*?data-valueid=\"(.*?)\"\shref=\"/\w+(.*?)\"\srel=\"(.*?)\">(.*?)</a>*",
                                    str(brand_content))

            for v in brands:
                brand_id = v[0]
                brand_url = v[1]
                brand_name = v[3]

                # 组装品牌URL列表
                brand_url_list.append(brand_url)

                # 组装品牌记录入库
                tablename = 'brandinfo'
                data = dict()
                data.update(brand_id=brand_id)
                result = self.conn.isInRecord(tablename, data)
                if result:
                    continue
                else:
                    data.update(brand_id=brand_id, brand_name=brand_name.decode('unicode-escape'), brand_url=brand_url)
                    self.conn.insert(tablename, data)

            return brand_url_list
        except Exception as e:
            print "getBrand: " + str(e)

    def getModel(self, url):
        # TODO: 实现获取车辆品牌下的所有型号
        model_url_list = []
        model_soup = BeautifulSoup(requests.get(url).content, "html.parser")
        model_content = model_soup.find_all("a", class_="search_search_click preventdefault")
        models = re.findall("<a.*?data-valueid=\"(.*?)\"\shref=\"/\w+(.*?)\"\stitle=\"(.*?)\">(.*?)</a>", str(model_content))

        for v in models:
            model_id = v[0]
            model_url = v[1]
            model_name = v[3]

            # 组装型号URL列表
            model_url_list.append(model_url)

            # 组装品牌记录入库
            tablename = 'modelinfo'
            data = dict()
            data.update(model_id=model_id)
            result = self.conn.isInRecord(tablename, data)
            if result:
                continue
            else:
                data.update(model_id=model_id, model_name=model_name.decode('unicode-escape'), model_url=model_url)
                self.conn.insert(tablename, data)

        return model_url_list

        print model_url


    def loopIndexPage(self, city_url_list, brand_url_list):
        model_url_list = []
        # 循环所有页面组合
        if self.FLAG == 1:
            for city in city_url_list:
                self.getIndexPage(self.BASE_URL + city + "s/")
        elif self.FLAG == 2:
            for city in city_url_list:
                for brand in brand_url_list:
                    self.getIndexPage(self.BASE_URL + city + brand)
        elif self.FLAG == 3:
            for city in city_url_list:
                for brand in brand_url_list:
                    model_url_list.append(self.getModel(self.BASE_URL + city + brand))
                break

            for model_url in model_url_list:
                for url in model_url:
                    self.getIndexPage(self.BASE_URL + city + url)
        else:
            print "Error."

    def getIndexPage(self, url):
        try:
            car_id_list = []
            car_url_list = []
            car_content = []

            index_soup = BeautifulSoup(requests.get(url).content, "html.parser")
            # driver = self.driver
            # driver.get(url)
            # index_soup = BeautifulSoup(driver.page_source, "html.parser")

            # 寻找是否有下一页，如果有则递归抓取
            next_page = self.getNextPage(index_soup)
            if next_page:
                self.getIndexPage(next_page)

            print "current URL: " + url
            is_empty = index_soup.find_all("div", class_="err-show change-top")

            if is_empty:
                print "No car in the page."
            else:
                car_summer_list = index_soup.find_all("li", class_="con ")
                for car_summer in car_summer_list:
                    # 获取当前页面所有车辆URL
                    car_content = car_summer.select("h2 > a")
                    if not car_content:
                        car_content = car_summer.select(".aimg")

                    car_id_list.append(filter(str.isdigit, re.findall("carid=\"\d*\"", str(car_content[0]))[0]))
                    car_url_list.append(self.BASE_URL + re.findall("/\D*\d*.html", str(car_content[0]))[0])

                city_id = filter(str.isdigit, re.findall("cityid=\"\d*\"", str(car_content[0]))[0])
                car_dic = dict(zip(car_id_list, car_url_list))
                print car_dic
                self.getDetailPage(car_dic, city_id)

        except Exception as e:
            print "getIndexPage: " + str(e)

    def getNextPage(self, soup):
        next_page = soup.find_all("a", text="下一页")
        if next_page:
            next_page = re.findall("/\w+/s/\w\d+/", str(next_page))
            return self.BASE_URL + next_page[0]
        else:
            return None

    def getDetailPage(self, car_dic, city_id):
        tablename = 'carsummer'
        # driver = self.driver

        try:
            for car_id, car_url in car_dic.iteritems():
                # 抓去前检查是否已入库
                data = dict()
                data.update(car_id=car_id)
                result = self.conn.isInRecord(tablename, data)

                if result:
                    print car_id + " is exist."
                    continue
                else:
                    print car_url

                    # 提取车辆信息
                    # driver.get(car_url)
                    car_soup = BeautifulSoup(requests.get(car_url).content, "html.parser")
                    # car_soup = BeautifulSoup(driver.page_source, "html.parser")
                    car_brand = car_soup.select('.cd_m_h ')
                    car_title = car_brand[0].get_text().replace('\n', '')

                    car_price = car_soup.select('.cd_m_info b')
                    full_price = car_price[0].get_text().replace(u'万', '').replace(u'￥', '')
                    if len(car_price) == 2:
                        is_FYB = 1
                    else:
                        is_FYB = 0

                    car_info = car_soup.select('.cd_m_info_desc span')
                    license_date = car_info[2].get_text() + '-01'
                    sale_date = car_info[4].get_text()
                    meters = car_info[0].get_text().replace(u'万公里', '')
                    meters = self.tools.format(meters)
                    displacement = car_info[6].get_text()
                    effluent = car_info[8].get_text()

                    if car_soup.select('.cd_m_info_cover_ys'):
                        is_onsale = 0
                    else:
                        is_onsale = 1

                    # 组装车辆信息
                    data = dict()
                    data.update(car_id=car_id, car_title=car_title, license_date=license_date, sale_date=sale_date,
                                displacement=displacement, is_FYB=is_FYB, effluent=effluent, meters=meters,
                                full_price=full_price, city_id=city_id, is_onsale=is_onsale)
                    self.conn.insert(tablename, data)

        except Exception as e:
            print "DetailPage: " + str(e)


if __name__ == '__main__':
    cp = ConfigParser.ConfigParser()
    cp.read(os.getcwd() + "\\resource\\spider.conf")

    # TODO: 配置文件读取初始URL及数据库连接等
    # 初始化配置
    db_conf = cp.items('db')
    db_conf = dict(db_conf)
    phantomjs = cp.get('phantomjs', 'windows')
    city_url = cp.get('url', 'city_url')
    brand_url = cp.get('url', 'brand_url')
    model_url = cp.get('url', 'model_url')

    spider = YouXin(db_conf, phantomjs)

    city_url_list = spider.getCity(city_url)
    brand_url_list = spider.getBrand(brand_url)
    spider.loopIndexPage(city_url_list, brand_url_list)
