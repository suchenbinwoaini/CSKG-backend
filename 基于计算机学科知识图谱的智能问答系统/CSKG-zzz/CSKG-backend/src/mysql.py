from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql

db = pymysql.connect(host="localhost", user="root", password="123456", database="test")


class SqlDB:
    def __init__(self):
        try:
            self.db = pymysql.connect(host="localhost", user="root", password="123456", database="cs_map")
            # 游标对象
            self.cursor = self.db.cursor()
            print("连接成功！")
        except:
            print("连接失败！")

    def getdata(self):
        sql = "select * from answer"
        # 执行sql语句
        self.cursor.execute(sql)
        # 获取所有的记录
        result = self.cursor.fetchall()
        fields = self.cursor.description
        res = self.format_data(fields, result)
        print(res)
        return res

    def format_data(self, fields, result):
        # 字段数组 ['id', 'name', 'password']
        field = []
        for i in fields:
            field.append(i[0])
        # 返回的数组集合 形式[{'id': 1, 'name': 'admin', 'password': '123456'}]
        res = []
        for iter in result:
            line_data = {}
            for index in range(0, len(field)):
                line_data[field[index]] = iter[index]
            res.append(line_data)
        return res

    # def set_answer(self,answer):




    # 关闭
    def __del__(self):
        self.db.close()
