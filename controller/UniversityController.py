from flask import request, session, render_template, Blueprint, jsonify
from service.UniversityService import UniversityService

# 定义UniversityController蓝图，用于处理与大学相关的HTTP请求
universityController = Blueprint('UniversityController', __name__)
universityService = UniversityService()  # 实例化UniversityService对象，用于调用服务层方法


# 返回JSON格式的所有大学数据
@universityController.route('/getalluniversities', methods=['GET', 'POST'])
def get_all_universities():
    """
    获取所有大学信息，并以JSON格式响应。

    请求方式: GET 或 POST

    响应格式: {"universities": [{university_data}, {university_data}, ...]}
    """
    all_universities = universityService.getAllUniversities()  # 调用UniversityService的getAllUniversities方法获取所有大学数据
    return jsonify(all_universities)  # 使用jsonify将大学数据转化为JSON响应


# 创建大学
@universityController.route('/createuniversity', methods=['POST'])
def create_university():
    """
    创建新大学。

    请求方式: POST
    请求参数: application/x-www-form-urlencoded 或 multipart/form-data

    请求参数示例:
    {
        "name": "Example University",
        "fullname": "Example University of Science and Technology",
        "api": "https://example.edu/api"
    }

    响应格式: {"success": True/False}
    """
    # 从请求中获取大学信息
    name = request.form.get('name')
    fullname = request.form.get('fullname')
    api = request.form.get('api')
    # uni_id = request.form.get('uni_id')

    # 调用UniversityService中的方法创建大学
    result = universityService.createUniversity(name, fullname, api)

    # 返回创建结果
    return jsonify({"success": result})


# 删除大学
@universityController.route('/deleteuniversity/<int:uni_id>', methods=['DELETE'])
def delete_university(uni_id):
    """
    删除指定ID的大学。

    请求方式: DELETE
    请求路径参数: uni_id (大学ID，整数)

    响应格式: {"success": True/False}
    """
    # 调用UniversityService中的方法删除大学
    result = universityService.deleteUniversityById(uni_id)

    # 返回删除结果
    return jsonify({"success": result})


# 更新大学信息
@universityController.route('/updateuniversity/<int:uni_id>', methods=['PUT'])
def update_university(uni_id):
    """
    更新指定ID大学的部分或全部信息。

    请求方式: PUT
    请求路径参数: uni_id (大学ID，整数)
    请求参数: application/x-www-form-urlencoded 或 multipart/form-data

    请求参数示例:
    {
        "name": "New University Name",
        "fullname": "New University of Science and Technology",
        "api": "https://new.example.edu/api"
    }

    响应格式: {"success": True/False}
    """
    # 从请求中获取更新的大学信息
    name = request.form.get('name')
    fullname = request.form.get('fullname')
    api = request.form.get('api')

    # 调用UniversityService中的方法更新大学信息
    result = universityService.updateUniversityById(uni_id, name, fullname, api)

    # 返回更新结果
    return jsonify({"success": result})


# 获取特定大学信息
@universityController.route('/getuniversity/<int:uni_id>', methods=['GET'])
def get_university(uni_id):
    """
    获取指定ID大学的详细信息。

    请求方式: GET
    请求路径参数: uni_id (大学ID，整数)

    响应格式: {"university": {university_data}}
    """
    # 调用UniversityService中的方法获取特定大学信息
    university_info = universityService.getUniversityById(uni_id)

    # 返回大学信息
    return jsonify(university_info)
