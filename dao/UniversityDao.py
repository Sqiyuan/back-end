from dao.BaseDao import BaseDao


# 大学数据管理数据库操作类   DAO：database access object
class UniversityDao(BaseDao):
    """
   大学数据管理数据库操作类，继承自BaseDao，提供了针对university表的CRUD操作。

   方法：
   - createUniversity(self, params=[]): 创建大学记录。
   - deleteUniversityById(self, uni_id): 根据uni_id删除大学。
   - updateUniversityById(self, params=[]): 根据uni_id更新大学信息。
   - getUniversityById(self, uni_id): 根据uni_id查询大学信息。
   - getAllUniversities(self): 获取所有大学的信息。
   """

    def createUniversity(self, params=[]):
        """
        创建大学记录。

        参数:
        - params (list): 包含大学信息的参数列表，格式为[name, fullname, api]。

        返回: int，表示插入数据影响的行数。
        """
        sql = "INSERT INTO university (name, fullname, api) VALUES (%s, %s, %s)"
        result = self.execute(sql, params)
        self.commit()
        return result

    def deleteUniversityById(self, uni_id):
        """
        根据uni_id删除大学。

        参数:
        - uni_id (int): 大学的唯一标识符。

        返回: int，表示删除数据影响的行数。
        """
        sql = "DELETE FROM university WHERE uni_id = %s"
        result = self.execute(sql, [uni_id])
        self.commit()
        return result

    def updateUniversityById(self, params=[]):
        """
        根据uni_id更新大学信息。

        参数:
        - params (list): 包含更新信息的参数列表，格式为[name, fullname, api, uni_id]。

        返回: int，表示更新数据影响的行数。
        """
        sql = "UPDATE university SET name = %s, fullname = %s, api = %s WHERE uni_id = %s"
        result = self.execute(sql, params)
        self.commit()
        return result

    def getUniversityById(self, uni_id):
        """
        根据uni_id查询大学信息。

        参数:
        - uni_id (int): 大学的唯一标识符。

        返回: list of dict，包含查询结果的列表，每个元素为字典形式的大学信息。
        """
        sql = "SELECT * FROM university WHERE uni_id = %s"
        self.execute(sql, [uni_id])
        resultSet = self.fetchall()
        return resultSet

    def getAllUniversities(self):
        """
        获取所有大学的信息。

        参数: 无

        返回: list of dict，包含所有大学信息的列表，每个元素为字典形式的大学信息。
        """
        sql = "SELECT * FROM university"
        self.execute(sql)
        resultSet = self.fetchall()
        return resultSet
