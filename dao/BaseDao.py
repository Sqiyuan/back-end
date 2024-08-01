import pymysql
import json
import os

class BaseDao():
    """
    数据库访问基类，封装了与MySQL数据库连接、执行SQL语句、获取结果、关闭连接等基本操作。

    属性：
    - __config (dict): 从`mysql.json`配置文件加载的数据库连接参数。
    - __conn (pymysql.Connection): 与MySQL数据库建立的连接对象，用于执行SQL语句。
    - __cursor (pymysql.cursors.Cursor): 用于执行SQL语句并获取结果的游标对象。

    方法：
    - __init__(self, config="mysql.json"): 构造函数，读取配置文件并初始化连接相关属性。
    - getConnection(self): 获取数据库连接，若尚未建立连接则创建新的连接。
    - execute(self, sql, params=[], ret="dict"): 执行SQL语句，可指定参数列表和返回结果类型（默认为字典）。
    - fetchone(self): 获取执行SQL后下一行结果。
    - fetchall(self): 获取执行SQL后所有结果。
    - close(self): 关闭游标和连接，释放资源。
    - commit(self): 提交事务。
    - rollback(self): 回滚事务。
    """
    def __init__(self, config="mysql.json"):
        """
        初始化BaseDao对象，读取`mysql.json`配置文件，设置连接参数。
        参数:
        - config (str): 配置文件路径，默认为"mysql.json"。
        返回: 无
        """
        self.__config = json.load(open(config, mode="r", encoding="utf-8"))  # 读取mysql.json配置文件，转为python对象
        self.__conn = None
        self.__cursor = None

        pass

    def getConnection(self):
        """
        获取与MySQL数据库的连接。如果已有连接存在，则直接返回；否则新建连接。
        参数: 无
        返回: pymysql.Connection 对象，表示与数据库的连接。
        """
        if self.__conn != None:
            return self.__conn
        self.__conn = pymysql.connect(**self.__config)   # **{"host":"127.0.0.1", "user":"root", "password":"root", "database":"db_jobsdata", "port":3306, "charset":"utf8"}
        return self.__conn

    def execute(self, sql , params=[], ret="dict"):
        """
        执行SQL语句，可指定参数列表和返回结果类型（默认为字典）。

        参数:
        - sql (str): 待执行的SQL语句。
        - params (list): SQL语句参数列表，默认为空。
        - ret (str): 返回结果类型，可选值为"dict"（默认，返回字典）或其它（返回元组）。

        返回: int，表示执行SQL语句影响的行数。
        """
        result = 0
        try:
            self.__conn = self.getConnection()
            if ret == "dict":
                self.__cursor = self.__conn.cursor(pymysql.cursors.DictCursor)  # 返回字典数据
            else:
                self.__cursor = self.__conn.cursor()                            # 返回元组数据
            result = self.__cursor.execute(sql, params)
        except pymysql.DatabaseError as e:
            print(e)
        return result

    def fetchone(self):
        """
        获取执行SQL后下一行结果。
        参数: 无
        返回: 字典（默认）或元组，表示执行SQL后下一行结果。如果没有更多数据，则返回None。
        """
        if self.__cursor:
            return self.__cursor.fetchone()

    def fetchall(self):
        """
        获取执行SQL后所有结果。
        参数: 无
        返回: 列表，其中每个元素为字典（默认）或元组，表示执行SQL后的一行结果。如果没有数据，则返回空列表。
        """
        if self.__cursor:
            return self.__cursor.fetchall()

    def close(self):
        """
        关闭游标和连接，释放资源。
        参数: 无
        返回: 无
        """
        if self.__cursor:
            self.__cursor.close()

        if self.__conn:
            self.__conn.close()

    def commit(self):
        """
        提交事务。
        参数: 无
        返回: 无
        """
        if self.__conn:
            self.__conn.commit()

    def rollback(self):
        """
        回滚事务。
        参数: 无
        返回: 无
        """
        if self.__conn:
            self.__conn.rollback()

if __name__ == '__main__':
    bD = BaseDao()
