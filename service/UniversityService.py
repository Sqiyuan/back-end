from dao.UniversityDao import UniversityDao


class UniversityService():
    """
    UniversityService类，封装了对大学数据的操作逻辑，通过UniversityDao与数据库交互。

    方法：
    - getAllUniversities(self): 获取所有大学信息。
    - createUniversity(self, name, fullname, api): 创建大学。
    - deleteUniversityById(self, uni_id): 根据大学ID删除大学。
    - updateUniversityById(self, uni_id, name, fullname, api): 根据大学ID更新大学信息。
    - getUniversityById(self, uni_id): 根据大学ID查询大学信息。
    """

    def getAllUniversities(self):
        """
        获取所有大学信息。

        参数: 无

        返回: list of dict，包含所有大学信息的列表，每个元素为字典形式的大学信息。
        """
        universityDao = UniversityDao()  # 创建UniversityDao实例
        try:
            resultSet = universityDao.getAllUniversities()  # 调用UniversityDao的getAllUniversities方法获取所有大学信息
        finally:
            universityDao.close()  # 关闭数据库连接
        return resultSet

    def createUniversity(self, name, fullname, api):
        """
        创建大学。

        参数:
        - name (str): 大学名称。
        - fullname (str): 大学全称。
        - api (str): 大学API接口地址。

        返回: int，表示插入数据影响的行数。
        """
        universityDao = UniversityDao()
        try:
            params = [name, fullname, api]  # 构造参数列表
            result = universityDao.createUniversity(params)  # 调用UniversityDao的createUniversity方法创建大学
        finally:
            universityDao.close()  # 关闭数据库连接
        return result

    def deleteUniversityById(self, uni_id):
        """
       根据大学ID删除大学。

       参数:
       - uni_id (int): 大学的唯一标识符。

       返回: int，表示删除数据影响的行数。
       """
        universityDao = UniversityDao()
        try:
            result = universityDao.deleteUniversityById(uni_id)  # 调用UniversityDao的deleteUniversityById方法删除大学
        finally:
            universityDao.close()
        return result

    def updateUniversityById(self, uni_id, name, fullname, api):
        """
        根据大学ID更新大学信息。

        参数:
        - uni_id (int): 大学的唯一标识符。
        - name (str): 更新后的大学名称。
        - fullname (str): 更新后的大学全称。
        - api (str): 更新后的大学API接口地址。

        返回: int，表示更新数据影响的行数。
        """
        universityDao = UniversityDao()
        try:
            params = [name, fullname, api, uni_id]
            result = universityDao.updateUniversityById(params)  # 调用UniversityDao的updateUniversityById方法更新大学信息
        finally:
            universityDao.close()
        return result

    def getUniversityById(self, uni_id):
        """
        根据大学ID查询大学信息。

        参数:
        - uni_id (int): 大学的唯一标识符。

        返回: list of dict，包含查询结果的列表，每个元素为字典形式的大学信息。
        """
        universityDao = UniversityDao()
        try:
            resultSet = universityDao.getUniversityById(uni_id)  # 调用UniversityDao的getUniversityById方法查询大学信息
        finally:
            universityDao.close()
        return resultSet
