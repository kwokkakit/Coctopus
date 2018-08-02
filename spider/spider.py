#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import abc

class Spider(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def getCity(self):
        """获取城市信息以及URL"""
        pass

    @abc.abstractmethod
    def getBrand(self):
        """获取品牌信息以及URL"""
        pass

    @abc.abstractmethod
    def getModel(self):
        """获取车辆型号"""
        pass

    @abc.abstractmethod
    def getIndexPage(self):
        """获取车辆筛选结果内容"""
        pass

    @abc.abstractmethod
    def getDetailPage(self):
        """获取车辆信息内容"""
        pass