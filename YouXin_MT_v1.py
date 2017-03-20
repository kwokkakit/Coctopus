#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from bs4 import BeautifulSoup
from selenium import webdriver
import re
import requests
import logging

import db, common

class YouXin():
    def __init__(self):
        # 使用PhantomJS获取渲染后页面
        self.driver = webdriver.PhantomJS(executable_path="C:\\Program Files (x86)\\Phantomjs\\bin\\phantomjs.exe")

        # 初始化公共变量
        self.BASE_URL = "http://www.xin.com"

        # 初始化数据库连接
        self.db = db.DBHandler(
            {'host': 'localhost', 'port': 3306, 'user': 'root', 'passwd': '', 'db': 'youxin', 'charset': 'utf8'})

        # 初始化基础工具
        self.tools = common.BaseFunction()

        # 初始化多线程
        self.NUM_OF_THREADS = 40

    def getLocation(self, locatoin_page):
        try:
            driver = self.driver
            driver.get(locatoin_page)

            # 提取页面中的城市
            location_soup = BeautifulSoup(driver.page_source, "lxml")
            location_content = location_soup.find_all("div", class_='ci_m_city ci_m_list')
            location_url = re.findall("<a\scityid=\"\d*\"\shref=\"/(.*?)/\">*", str(location_content))
            location_city = re.findall("<a\s*cityid\s*=\s*\"[0-9]*\"\shref=['\"]/\w*/['\"]>(.*?)</a>*",
                                       str(location_content))
            location_id = re.findall("cityid=\"\d*\"\shref", str(location_content))
        except Exception as e:
            print "Location" + str(e)

        # 拼接URL
        for _key, _value in enumerate(location_url):
            location_url[_key] = self.BASE_URL + '/' + _value + '/s/'

        # 提取城市ID
        for _key, _value in enumerate(location_id):
            location_id[_key] = re.findall("\d+", _value, re.M)[0]

        # 组装城市记录入库
        for i in range(len(location_id)):
            data = dict()
            data.update(city_id=location_id[i])
            result = self.db.isInRecord('cityinfo', data)
            if result:
                continue
            else:
                data.update(city_id=location_id[i], city_name=location_city[i].decode('unicode-escape'),
                            city_url=location_url[i])
                self.db.insert('cityinfo', data)

        location_dic = dict(zip(location_id, location_url))

        return location_dic

    def cityIndexPage(self, location_dic):
        # 循环所有城市
        for k, v in location_dic.iteritems():
            self.getIndexPage(v)

    def getIndexPage(self, url):
        try:
            car_id_list = []
            car_url_list = []
            car_content = []

            # index_soup = BeautifulSoup(requests.get(url).content, "html.parser")
            driver = self.driver
            driver.get(url)

            index_soup = BeautifulSoup(driver.page_source, "html.parser")

            # 寻找是否有下一页，如果有则递归抓取
            next_page = self.getNextPage(index_soup)
            if next_page:
                self.getIndexPage(next_page)

            print "current URL: " + url
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
        wm = common.WorkManager(self.NUM_OF_THREADS)

        try:
            for car_id, car_url in car_dic.iteritems():
                # 抓去前检查是否已入库
                data = dict()
                data.update(car_id=car_id)
                result = self.db.isInRecord('carsummer', data)

                if result:
                    print car_id + " is exist."
                    continue
                else:
                    print car_url

                    # 多线程抓取详细页面
                    wm.add_job(self.getCarInfo, car_id, car_url, city_id)
            wm.start()
            wm.wait_for_complete()

        except Exception as e:
            print "DetailPage: " + str(e)

    def getCarInfo(self, car_id, car_url, city_id):
        #多线程单独申请资源
        driver = webdriver.PhantomJS(executable_path="C:\\Program Files (x86)\\Phantomjs\\bin\\phantomjs.exe")
        conn = db.DBHandler(
            {'host': 'localhost', 'port': 3306, 'user': 'root', 'passwd': '', 'db': 'youxin', 'charset': 'utf8'})

        # 提取车辆信息
        driver.get(car_url)
        car_soup = BeautifulSoup(driver.page_source, "html.parser")
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

        print data
        conn.insert('carsummer', data)

        #关闭浏览器和关闭数据库连接
        driver.quit()
        conn.close()

if __name__ == '__main__':
    test = YouXin()
    a = test.getLocation("http://m.xin.com/location/index/beijing/")
    test.cityIndexPage(a)
