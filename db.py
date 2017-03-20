#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import MySQLdb
import time


class DBHandler:
    # 对MySQLdb常用函数进行封装的类

    error_code = ''  # MySQL错误号码

    _instance = None  # 本类的实例
    _conn = None  # 数据库conn
    _cur = None  # 游标

    _TIMEOUT = 30  # 默认超时30秒
    _timecount = 0

    def __init__(self, dbconfig):
        # 构造器：根据数据库连接参数，创建MySQL连接'
        try:
            """
            dbconfig = {  'host':'localhost',
                            'user':'root',
                            'passwd':'root',
                            'db':'others',
                            'charset':'utf8'}
            """
            self._conn = MySQLdb.connect(host=dbconfig['host'],
                                         port=dbconfig['port'],
                                         user=dbconfig['user'],
                                         passwd=dbconfig['passwd'],
                                         db=dbconfig['db'],
                                         charset=dbconfig['charset'])
        except MySQLdb.Error, e:
            self.error_code = e.args[0]
            error_msg = 'MySQL error! ', e.args[0], e.args[1]
            print error_msg

            # 如果没有超过预设超时时间，则再次尝试连接，
            if self._timecount < self._TIMEOUT:
                interval = 5
                self._timecount += interval
                time.sleep(interval)
                return self.__init__(dbconfig)
            else:
                raise Exception(error_msg)

        self._cur = self._conn.cursor()
        self._instance = MySQLdb

    @staticmethod
    def escape(string):
        return '%s' % string

    def query(self, sql_query=''):
        # 执行 SELECT 语句
        try:
            self._cur.execute("SET NAMES utf8")
            result = self._cur.execute(sql_query)
        except MySQLdb.Error, e:
            self.error_code = e.args[0]
            print "数据库错误代码:", e.args[0], e.args[1]
            result = False
        return result

    def update(self, sql_query=''):
        # 执行 UPDATE 及 DELETE 语句
        try:
            self._cur.execute("SET NAMES utf8")
            result = self._cur.execute(sql_query)
            self._conn.commit()
        except MySQLdb.Error, e:
            self.error_code = e.args[0]
            print "数据库错误代码:", e.args[0], e.args[1]
            result = False
        return result

    def insert(self, tablename=None, values={}):
        # 执行 INSERT 语句。如主键为自增长int，则返回新生成的ID
        if self._conn:
            tablename = self.escape(tablename)
            if values:
                _keys = ",".join(self.escape(k) for k in values)
                _values = ",".join(['%s', ] * len(values))
                sql_query = "INSERT INTO %s (%s) VALUE (%s)" % (tablename, _keys, _values)
            else:
                return False
            try:
                # print sql_query
                # print list(values.itervalues())
                self._cur.execute("SET NAMES 'utf8'")
                self._cur.execute(sql_query, list(values.itervalues()))
                self._conn.commit()
                return self._conn.insert_id()
            except MySQLdb.Error, e:
                self.error_code = e.args[0]
            return False
        else:
            raise ValueError
            return False

    def fetchAllRows(self):
        # 返回结果列表
        return self._cur.fetchall()

    def fetchOneRow(self):
        # 返回一行结果，然后游标指向下一行。到达最后一行以后，返回None
        return self._cur.fetchone()

    def getRowCount(self):
        # 获取结果行数
        return self._cur.rowcount

    def isInRecord(self, tablename=None, condition={}):
        # 判断记录是否已在数据库中
        if self._conn and condition:
            tablename = self.escape(tablename)
            _field, _value = condition.popitem()
            sql_query = "SELECT * FROM `%s` WHERE %s = %s" % (tablename, _field, _value)
            try:
                self._cur.execute("SET NAMES utf8")
                result = self._cur.execute(sql_query)
            except MySQLdb.Error, e:
                self.error_code = e.args[0]
                print "数据库错误代码:", e.args[0], e.args[1]
                result = False
            return result
        else:
            raise ValueError
            return 0

    def commit(self):
        # 数据库commit操作
        self._conn.commit()

    def rollback(self):
        # 数据库回滚操作
        self._conn.rollback()

    def __del__(self):
        # 释放资源（系统GC自动调用）
        try:
            self._cur.close()
            self._conn.close()
        except Exception as e:
            print "Mysql error: " + str(e)

    def close(self):
        # 关闭数据库连接
        self.__del__()