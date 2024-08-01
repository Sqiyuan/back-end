from flask import request, session, render_template, Blueprint, jsonify
from service.UserService import UserService

# 定义UserController蓝图，用于处理与用户相关的HTTP请求
userController = Blueprint('UserController', __name__)
userService = UserService()  # 实例化UserService对象，用于调用服务层方法


# 蓝图路由：返回JSON格式的所有用户数据
@userController.route('/getalluser', methods=['GET', 'POST'])
def get_all_users():
    """
    获取所有用户信息，并以JSON格式响应。

    请求方式: GET 或 POST

    响应格式: {"users": [{user_data}, {user_data}, ...]}
    """
    all_users = userService.getAllUsers()  # 调用UserService的getAllUsers方法获取所有用户数据
    return jsonify(all_users)  # 使用jsonify将用户数据转化为JSON响应


# 创建用户
@userController.route('/createuser', methods=['POST'])
def create_user():
    """
    创建新用户。

    请求方式: POST
    请求参数: application/x-www-form-urlencoded 或 multipart/form-data

    请求参数示例:
    {
        "username": "example_username",
        "password": "example_password",
        "name": "Example Name",
        "stu_num": "123456",
        "pho_num": "1234567890"
    }

    响应格式: {"success": True/False}
    """
    # 从请求中获取用户信息
    username = request.form.get('username')
    password = request.form.get('password')
    uni_id = 0
    name = request.form.get('name')
    stu_num = request.form.get('stu_num')
    pho_num = request.form.get('pho_num')

    # 调用UserService中的方法创建用户
    result = userService.createUser(username, password, uni_id, name, stu_num, pho_num)

    # 返回创建结果
    return jsonify({"success": result})


# 删除用户
@userController.route('/deleteuser/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    删除指定ID的用户。

    请求方式: DELETE
    请求路径参数: user_id (用户ID，整数)

    响应格式: {"success": True/False}
    """
    # 调用UserService中的方法删除用户
    result = userService.deleteUserById(user_id)

    # 返回删除结果
    return jsonify({"success": result})


# 更新用户信息
@userController.route('/updateuser/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    更新指定ID用户的部分或全部信息。

    请求方式: PUT
    请求路径参数: user_id (用户ID，整数)
    请求参数: application/x-www-form-urlencoded 或 multipart/form-data

    请求参数示例:
    {
        "username": "new_username",
        "password": "new_password",
        "name": "New Name",
        "stu_num": "654321",
        "pho_num": "0987654321"
    }

    响应格式: {"success": True/False}
    """
    # 从请求中获取更新的用户信息
    username = request.form.get('username')
    password = request.form.get('password')
    uni_id = 0
    name = request.form.get('name')
    stu_num = request.form.get('stu_num')
    pho_num = request.form.get('pho_num')

    # 调用UserService中的方法更新用户信息
    result = userService.updateUserById(user_id, username, password, uni_id, name, stu_num, pho_num)

    # 返回更新结果
    return jsonify({"success": result})


# 获取特定用户信息
@userController.route('/getuser/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    获取指定ID用户的详细信息。

    请求方式: GET
    请求路径参数: user_id (用户ID，整数)

    响应格式: {"user": {user_data}}
    """
    # 调用UserService中的方法获取特定用户信息
    user_info = userService.get_user_by_id(user_id)

    # 返回用户信息
    return jsonify(user_info)
