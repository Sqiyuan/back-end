from dao.UserDao import UserDao


class UserService():
    """
    UserService类，封装了对用户数据的操作逻辑，通过UserDao与数据库交互。

    方法：
    - getAllUsers(self): 获取所有用户信息。
    - createUser(self, username, password, uni_id, name, stu_num, pho_num): 创建用户。
    - deleteUserById(self, user_id): 根据用户ID删除用户。
    - updateUserById(self, user_id, username, password, uni_id, name, stu_num, pho_num): 根据用户ID更新用户信息。
    - getUserById(self, user_id): 根据用户ID查询用户信息。
    """

    def getAllUsers(self):
        """
        获取所有用户信息。

        参数: 无

        返回: list of dict，包含所有用户信息的列表，每个元素为字典形式的用户信息。
        """
        userDao = UserDao()  # 创建UserDao实例
        try:
            resultSet = userDao.getAllUser()  # 调用UserDao的getAllUser方法获取所有用户信息
        finally:
            userDao.close()  # 关闭数据库连接
        return resultSet  # 返回查询结果

    def createUser(self, username, password, uni_id, name, stu_num, pho_num):
        """
        创建用户。

        参数:
        - username (str): 用户名。
        - password (str): 密码。
        - uni_id (int): 用户所属大学ID。
        - name (str): 用户姓名。
        - stu_num (str): 学号。
        - pho_num (str): 手机号码。

        返回: int，表示插入数据影响的行数。
        """
        userDao = UserDao()
        try:
            params = [username, password, uni_id, name, stu_num, pho_num]  # 构造参数列表
            result = userDao.createUser(params)  # 调用UserDao的createUser方法创建用户
        finally:
            userDao.close()
        return result

    def deleteUserById(self, user_id):
        """
        根据用户ID删除用户。

        参数:
        - user_id (int): 用户的唯一标识符。

        返回: int，表示删除数据影响的行数。
        """
        userDao = UserDao()
        try:
            result = userDao.deleteUserById(user_id)  # 调用UserDao的deleteUserById方法删除用户
        finally:
            userDao.close()
        return result

    def updateUserById(self, user_id, username, password, uni_id, name, stu_num, pho_num):
        """
        根据用户ID更新用户信息。

        参数:
        - user_id (int): 用户的唯一标识符。
        - username (str): 更新后的用户名。
        - password (str): 更新后的密码。
        - uni_id (int): 更新后的用户所属大学ID。
        - name (str): 更新后的用户姓名。
        - stu_num (str): 更新后的学号。
        - pho_num (str): 更新后的手机号码。

        返回: int，表示更新数据影响的行数。
        """
        userDao = UserDao()
        try:
            params = [username, password, uni_id, name, stu_num, pho_num, user_id]
            result = userDao.updateUserById(params)  # 调用UserDao的updateUserById方法更新用户信息
        finally:
            userDao.close()
        return result

    def getUserById(self, user_id):
        """
        根据用户ID查询用户信息。

        参数:
        - user_id (int): 用户的唯一标识符。

        返回: list of dict，包含查询结果的列表，每个元素为字典形式的用户信息。
        """
        userDao = UserDao()
        try:
            resultSet = userDao.getUserById(user_id)  # 调用UserDao的getUserById方法查询用户信息
        finally:
            userDao.close()
        return resultSet
