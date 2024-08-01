from dao.BaseDao import BaseDao


# 用户数据管理数据库操作类   DAO：database access object
class UserDao(BaseDao):
    """
    用户数据管理数据库操作类，继承自BaseDao，提供了针对user表的CRUD操作以及根据用户名查询用户信息的功能。

    方法：
    - createUser(self, params=[]): 创建用户记录。
    - deleteUserById(self, user_id): 根据user_id删除用户。
    - updateUserById(self, params=[]): 根据user_id更新用户信息。
    - getUserById(self, user_id): 根据user_id查询用户信息。
    - getAllUser(self): 获取所有用户的信息。
    - usernameMatch(self, username): 根据用户名查询用户信息。
    """

    def createUser(self, params=[]):
        """
        创建用户记录。

        参数:
        - params (list): 包含用户信息的参数列表，格式为[username, password, uni_id, name, stu_num, pho_num]。

        返回: int，表示插入数据影响的行数。
        """
        sql = "INSERT INTO user (username, password, uni_id, name, stu_num, pho_num) " \
              "VALUES (%s, %s, %s, %s, %s, %s)"
        result = self.execute(sql, params)
        self.commit()
        return result

    def deleteUserById(self, user_id):
        """
        根据user_id删除用户。

        参数:
        - user_id (int): 用户的唯一标识符。

        返回: int，表示删除数据影响的行数。
        """
        sql = "DELETE FROM user WHERE id = %s"
        result = self.execute(sql, [user_id])
        self.commit()
        return result

    def updateUserById(self, params=[]):
        """
        根据user_id更新用户信息。

        参数:
        - params (list): 包含更新信息的参数列表，格式为[username, password, uni_id, name, stu_num, pho_num, user_id]。

        返回: int，表示更新数据影响的行数。
        """
        sql = "UPDATE user SET username = %s, password = %s, uni_id = %s, name = %s, " \
              "stu_num = %s, pho_num = %s WHERE id = %s"
        result = self.execute(sql, params)
        self.commit()
        return result

    def getUserById(self, user_id):
        """
        根据user_id查询用户信息。

        参数:
        - user_id (int): 用户的唯一标识符。

        返回: list of dict，包含查询结果的列表，每个元素为字典形式的用户信息。
        """
        sql = "SELECT * FROM user WHERE id = %s"
        self.execute(sql, [user_id])
        resultSet = self.fetchall()
        return resultSet

    def getAllUser(self):
        """
        获取所有用户的信息。

        参数: 无

        返回: list of dict，包含所有用户信息的列表，每个元素为字典形式的用户信息。
        """
        sql = "SELECT * from user"
        self.execute(sql)
        resultSet = self.fetchall()
        return resultSet

    def usernameMatch(self, username):
        """
        根据用户名查询用户信息。

        参数:
        - username (str): 用户名。

        返回: list of dict，包含查询结果的列表，每个元素为字典形式的用户信息。
        """
        sql = "SELECT * FROM user WHERE username = %s"
        self.execute(sql, [username])
        resultSet = self.fetchall()
        return resultSet
