from dao.BookDao import BookDao


class BookService():
    """
    BookService类，封装了对图书数据的操作逻辑，通过BookDao与数据库交互。

    方法：
    - addBook(self, params): 添加新的图书信息。
    - deleteBook(self, book_id): 根据book_id删除图书。
    - updateBook(self, params): 根据book_id更新图书信息。
    - getBookById(self, book_id): 根据book_id查询图书信息。
    - getAllBooks(self): 获取所有图书信息。
    """

    def addBook(self, params):
        """
        添加新的图书信息。

        参数:
        - params (list): 包含图书信息的参数列表，格式为[label, title, uni_id, num_info]。

        返回: int，表示插入数据影响的行数。
        """
        bookDao = BookDao()  # 创建BookDao实例
        return bookDao.createBook(params)  # 调用BookDao的createBook方法添加图书

    def deleteBook(self, book_id):
        """
        根据book_id删除图书。

        参数:
        - book_id (int): 图书的唯一标识符。

        返回: int，表示删除数据影响的行数。
        """
        bookDao = BookDao()
        return bookDao.deleteBookById(book_id)  # 调用BookDao的deleteBookById方法删除图书

    # 根据book_id更新图书信息
    def updateBook(self, params):
        """
        根据book_id更新图书信息。

        参数:
        - params (list): 包含更新信息的参数列表，格式为[label, title, uni_id, num_info, book_id]。

        返回: int，表示更新数据影响的行数。
        """
        bookDao = BookDao()
        return bookDao.updateBookById(params)  # 调用BookDao的updateBookById方法更新图书信息

    def getBookById(self, book_id):
        """
        根据book_id查询图书信息。

        参数:
        - book_id (int): 图书的唯一标识符。

        返回: list of dict，包含查询结果的列表，每个元素为字典形式的图书信息。
        """
        bookDao = BookDao()
        return bookDao.getBookById(book_id)  # 调用BookDao的getBookById方法查询图书信息

    def getAllBooks(self):
        """
        获取所有图书信息。

        参数: 无

        返回: list of dict，包含所有图书信息的列表，每个元素为字典形式的图书信息。
        """
        bookDao = BookDao()
        try:
            resultSet = bookDao.getAllBooks()  # 调用BookDao的getAllBooks方法获取所有图书信息
        finally:
            bookDao.close()  # 如果BaseDao中有close方法用于关闭数据库连接，则在此处调用
        return resultSet
