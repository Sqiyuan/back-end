from flask import Flask, request, session, send_file, jsonify, render_template
from controller.UserController import userController
from controller.BookController import bookController
from controller.UniversityController import universityController

from utils.ImageExecute import *
from utils.OCR import *
from utils.Process import *
from PIL import Image
from threading import Thread
from dao.UserDao import UserDao
import json
import os
import base64

app = Flask(__name__)  # 导入Flask库并创建Flask应用实例
# 设置Flask应用的SECRET_KEY，用于启用session管理
app.config['SECRET_KEY'] = "AIWORKPROJECT123456789"  # 使用session必须配置

# 注册多个Blueprints以组织路由和视图
app.register_blueprint(userController)
app.register_blueprint(universityController)
app.register_blueprint(bookController)

# 全局变量，存储待查找的书名
book_name = ''


# 主页路由，返回'index.html'
@app.route('/')
def index():
    return "index.html"


# 检查处理结果是否已生成的路由（POST）
@app.route('/check', methods=['POST'])
def check():
    # 如果完成标志目录存在，返回'1'表示结果已生成
    if os.path.exists('finish.flag'):
        return json.dumps('1')
    # 否则返回'0'表示结果未生成
    return json.dumps('0')


# 启动处理线程的路由（GET/POST）
@app.route('/process', methods=['GET', 'POST'])
def process():
    # 清除已完成标志和输出目录（如果存在）
    if os.path.exists('finish.flag'):
        shutil.rmtree('finish.flag')
    if os.path.exists('output'):
        shutil.rmtree('output')

    # 创建输出目录
    os.mkdir('output')

    # 启动处理整个过程的线程
    thread = Thread(target=wholeProcess)
    thread.start()
    # 如果工作目录下无待处理文件，返回'0'表示无数据
    if len(os.listdir(dir)) == 0:
        return json.dumps('0')
    # 返回'1'表示处理线程已启动
    return json.dumps('1')


# 启动特定书籍查找过程的线程（GET/POST）
@app.route('/findbook', methods=['GET', 'POST'])
def findbookprocess():
    # 清除已完成标志和输出目录（如果存在）
    if os.path.exists('finish.flag'):
        shutil.rmtree('finish.flag')
    if os.path.exists('output'):
        shutil.rmtree('output')
    # 创建输出目录
    os.mkdir('output')
    # 启动针对指定书名的查找过程线程，传入全局变量`book_name`
    thread = Thread(target=findBookProces, args=(book_name,))
    thread.start()
    # 如果工作目录下无待处理文件，返回'0'表示无数据
    if len(os.listdir(dir)) == 0:
        return json.dumps('0')
    # 返回'1'表示查找线程已启动
    return json.dumps('1')


# 用户登录接口（POST）
@app.route('/login', methods=['POST'])
def login():
    res = dict()# 初始化响应字典
    # 从请求体中获取JSON数据
    data = request.json
    username = data.get('username')
    password = data.get('password')
    uniersity = data.get('uni_id')
    status = data.get('status')
    # 实例化UserDao类以进行数据库操作
    userDao = UserDao()
    # 检查用户名是否存在
    if not username:
        return json.dumps('1')

    # 使用UserDao查询与用户名匹配的用户信息
    userinfo = userDao.usernameMatch(username=username)

    # 校验用户状态、密码及所属大学ID
    if userinfo[0]['status'] != int(status):
        return json.dumps('2')
    if userinfo[0]['password'] != password:
        return json.dumps('3')
    if userinfo[0]['uni_id'] != int(uniersity):
        return json.dumps('4')

    # 登录成功，填充响应字典并返回
    res['result'] = '0'
    res['status'] = status
    return json.dumps(res)


# 图片上传接口（POST）
@app.route('/upload', methods=['POST'])
def upload():
    # 如果图片目录不存在，创建之
    if not os.path.exists('./img'):
        os.mkdir('./img')

    # 从请求体JSON中提取图片数据和文件名
    data = request.json
    img_base64 = data.get('img')
    img_name = data.get('url').split('/')[-1]

    # 如果请求包含书名，更新全局变量`book_name`
    if data.get('bookname'):
        global book_name
        book_name = data.get('bookname')
        print(book_name)

    # 检查图片数据是否存在
    if not img_base64:
        return json.dumps('0')

    # 保存图片到指定路径
    filepath = './img/' + img_name
    save_base64_image(img_base64, filepath)
    # 返回'1'表示图片上传成功
    return json.dumps('1')


@app.route('/result', methods=['GET'])
def result():
    """获取处理结果的接口（GET），以JSON形式返回输出目录中的图片数据"""
    img_folder = 'output'
    images_data = []
    # 遍历输出目录中的图片文件
    for filename in os.listdir(img_folder):
        if filename.endswith('.jpg') or filename.endswith('.png'):  # 假设图片为JPEG或PNG格式
            img_path = os.path.join(img_folder, filename)
            with open(img_path, 'rb') as img_file:
                img_data = img_file.read()
                base64_img = base64.b64encode(img_data).decode('utf-8')
                images_data.append({'filename': filename, 'image': base64_img})
    # 返回包含所有图片数据的JSON响应
    return jsonify({'images': images_data})


# 显示帮助页面的路由（GET）
@app.route('/help', methods=['GET'])
def help():
    return render_template('prenstation.html')


if __name__ == '__main__':
    # 初始化：清除并重新创建必要的文件夹
    const_files = ['img', 'output']
    const_removed_files = ['runs', 'finish.flag']
    const_all_files = const_files + const_removed_files
    for dir in const_all_files:
        if os.path.exists(dir):
            shutil.rmtree(dir)

    for dir in const_files:
        if not os.path.exists(dir):
            os.mkdir(dir)
    # app.run(host='172.20.10.2', debug=True)#手机热点          会启动Web应用服务，默认端口号是5000
    app.run(host='127.0.0.1', debug=True)  # 不用真机调试
    # app.run(host='10.11.25.198', debug=True)#家里
