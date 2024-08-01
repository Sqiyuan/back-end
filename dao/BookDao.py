from dao.BaseDao import BaseDao


# 图书数据管理数据库操作类   DAO：database access object
class BookDao(BaseDao):
    """
    图书数据管理数据库操作类，继承自BaseDao，提供了针对err_book表的CRUD操作。

    方法：
    - createBook(self, params=[]): 创建图书记录。
    - deleteBookById(self, book_id): 根据book_id删除图书。
    - updateBookById(self, params=[]): 根据book_id更新图书信息。
    - getBookById(self, book_id): 根据book_id查询图书信息。
    - getAllBooks(self): 获取所有图书的信息。
    """

    # 创建图书记录
    def createBook(self, params=[]):
        """
        创建图书记录。

        参数:
        - params (list): 包含图书信息的参数列表，格式为[label, title, uni_id, num_info]。

        返回: int，表示插入数据影响的行数。
        """
        sql = "INSERT INTO err_book (label, title, uni_id, num_info) VALUES (%s, %s, %s, %s)"
        result = self.execute(sql, params)
        self.commit()
        return result

    def deleteBookById(self, book_id):
        """
        根据book_id删除图书。

        参数:
        - book_id (int): 图书的唯一标识符。

        返回: int，表示删除数据影响的行数。
        """
        sql = "DELETE FROM err_book WHERE book_id = %s"
        result = self.execute(sql, [book_id])
        self.commit()
        return result

    def updateBookById(self, params=[]):
        """
        根据book_id更新图书信息。

        参数:
        - params (list): 包含更新信息的参数列表，格式为[label, title, uni_id, num_info, book_id]。

        返回: int，表示更新数据影响的行数。
        """
        sql = "UPDATE err_book SET label = %s, title = %s, uni_id = %s, num_info = %s WHERE book_id = %s"
        result = self.execute(sql, params)
        self.commit()
        return result

    def getBookById(self, book_id):
        """
        根据book_id查询图书信息。

        参数:
        - book_id (int): 图书的唯一标识符。

        返回: list of dict，包含查询结果的列表，每个元素为字典形式的图书信息。
        """
        sql = "SELECT * FROM err_book WHERE book_id = %s"
        self.execute(sql, [book_id])
        resultSet = self.fetchall()
        return resultSet

    def getAllBooks(self):
        """
        获取所有图书的信息。

        参数: 无

        返回: list of dict，包含所有图书信息的列表，每个元素为字典形式的图书信息。
        """
        sql = "SELECT * FROM err_book"
        self.execute(sql)
        resultSet = self.fetchall()
        return resultSet
