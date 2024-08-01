from flask import request, session, render_template, Blueprint, jsonify
from service.BookService import BookService

# 定义BookController蓝图，用于处理与图书相关的HTTP请求
bookController = Blueprint('BookController', __name__)
bookService = BookService()  # 实例化BookService对象，用于调用服务层方法


# 返回JSON格式的所有图书数据
@bookController.route('/getallbooks', methods=['GET', 'POST'])
def get_all_books():
    """
    获取所有图书信息，并以JSON格式响应。

    请求方式: GET 或 POST

    响应格式: {"books": [{book_data}, {book_data}, ...]}
    """
    all_books = bookService.getAllBooks()
    return jsonify(all_books)


# 创建图书
@bookController.route('/createbook', methods=['POST'])
def createBook():
    """
    创建新图书。

    请求方式: POST
    请求参数: application/x-www-form-urlencoded 或 multipart/form-data

    请求参数示例:
    {
        "label": "Example Label",
        "title": "Example Book Title",
        "uni_id": 123,
        "num_info": -1
    }

    注意: num_info字段默认为-1，在实际应用中可能需要从请求中获取该值。

    响应格式: {"success": True/False}
    """
    # 从请求中获取图书信息
    label = request.form.get('label')
    title = request.form.get('title')
    uni_id = request.form.get('uni_id')
    num_info = -1
    # num_info = request.form.get('num_info')

    params = [label, title, uni_id, num_info]  # 构建参数列表
    result = bookService.addBook(params)  # 调用BookService中的方法创建图书

    # 返回创建结果
    return jsonify({"success": result})


# 删除图书
@bookController.route('/deletebook/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    删除指定ID的图书。

    请求方式: DELETE
    请求路径参数: book_id (图书ID，整数)

    响应格式: {"success": True/False}
    """
    # 调用BookService中的方法删除图书
    result = bookService.deleteBook(book_id)

    # 返回删除结果
    return jsonify({"success": result})


# 更新图书信息
@bookController.route('/updatebook/<int:book_id>', methods=['PUT'])
def updateBook(book_id):
    """
    更新指定ID图书的部分或全部信息。

    请求方式: PUT
    请求路径参数: book_id (图书ID，整数)
    请求参数: application/x-www-form-urlencoded 或 multipart/form-data

    请求参数示例:
    {
        "label": "New Label",
        "title": "New Book Title",
        "uni_id": 456,
        "num_info": -1
    }

    注意: num_info字段默认为-1，在实际应用中可能需要从请求中获取该值。

    响应格式: {"success": True/False}
    """
    # 从请求中获取更新的图书信息
    label = request.form.get('label')
    title = request.form.get('title')
    uni_id = request.form.get('uni_id')
    num_info = -1
    # num_info = request.form.get('num_info')

    params = [label, title, uni_id, num_info, book_id]  # 构建参数列表
    result = bookService.updateBook(params)  # 调用BookService中的方法更新图书信息

    # 返回更新结果
    return jsonify({"success": result})


# 获取特定图书信息
@bookController.route('/getbook/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """
    获取指定ID图书的详细信息。

    请求方式: GET
    请求路径参数: book_id (图书ID，整数)

    响应格式: {"book": {book_data}}
    """
    # 调用BookService中的方法获取特定图书信息
    book_info = bookService.getBookById(book_id)

    # 返回图书信息
    return jsonify(book_info)
