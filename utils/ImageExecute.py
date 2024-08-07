import base64
import requests
from ultralytics import YOLO
from dao.BaseDao import BaseDao
import os
import cv2
import numpy as np
import shutil

dir = './img/'  # 待处理图像目录
result_dir = './runs/segment/predict/crops/book/'   # 预测结果保存目录
max_width = 400 # 图像最大宽度限制
book_name = '开始写吧'

model = YOLO('./ex_best.pt')    # 实例化YOLO模型，加载预训练权重


class BookDao(BaseDao):
    """
    职位数据管理数据库操作类
    DAO：database access object
    """
    # 获取book表中所有记录
    def getBooks(self):
        sql = 'select * from book'
        result = self.execute(sql=sql)
        resultSet = self.fetchall()
        return resultSet

def findLabelFromName(resultSet, character):
    """
    根据字符在结果集中查找标签匹配度超过75%的记录
    返回num_info；否则返回-1
    """
    for item in resultSet:
        count = 0
        length = len(character)
        for i in character:
            if i in item['label']:
                count += 1
            if count / length > 0.75:
                return item['num_info']
    return -1

def save_base64_image(data, file_path):
    """
    将Base64编码的图像数据保存到指定文件路径
    """
    try:
        # 提取并解码Base64数据
        base64_data = data
        binary_data = base64.b64decode(base64_data)
        # 将二进制数据写入文件
        with open(file_path, 'wb') as f:
            f.write(binary_data)
        print("图片保存成功")
    except Exception as e:
        print(f"图片保存失败: {e}")


def image_to_base64(image_path):
    """将图像文件转换为Base64编码字符串"""
    with open(image_path, "rb") as image_file:
        # 读取图片文件内容
        image_data = image_file.read()
        # 将图片内容编码为 base64 格式
        base64_encoded = base64.b64encode(image_data)
        # 将 bytes 类型转换为字符串类型
        base64_encoded_str = base64_encoded.decode('utf-8')
        return base64_encoded_str


def send_post_request(image_base64):
    """
    向指定URL发送POST请求，
    携带Base64编码的图像数据
    """
    # 请求的URL
    url = "http://127.0.0.1:8089/api/tr-run/"

    # 请求参数，包含图片的 base64 值
    data = {
        "img": image_base64,
        # "compress": "0"
    }
    try:
        # 发送 HTTP POST 请求
        response = requests.post(url, data=data)
        # # 打印响应信息
        # print("Status code:", response.status_code)
        # print("Response text:", response.text)
        return response
    except Exception as e:
        print("Error:", e)


def seq_to_filepath(filename, id, result_dir):
    """
    根据文件名、序号及结果目录生成完整文件路径
    如果id为0，则生成的文件路径为result_dir加上filename以及.jpg扩展名。
    否则，生成的文件路径为result_dir加上filename、(id+1)（表示序列编号）以及.jpg扩展名。
    """
    if id == 0:
        filepath = result_dir + str(filename) + '.jpg'
    else:
        filepath = result_dir + str(filename) + str(id + 1) + '.jpg'
    return filepath


def is_chinese_char(char):
    """
    判断字符是否为中文字符
    通过比较字符的Unicode编码是否在\u4e00（中文字符起始码点）到\u9fff（中文字符结束码点）之间来确定
    """
    # 检查字符的 Unicode 编码范围
    return '\u4e00' <= char <= '\u9fff'


def getSingleBookResult(http_json):
    """分析http返回的数据，返回该数的[标签数字，前七个字符]"""
    charatcter = ''  # 前七个字符
    num_str = ''  # 标签数字字符串
    lable_number = -1  # 标签数字
    character_count = 0  # 已收集的字符数

    for locate, element, conf in http_json['data']['raw_out']:
        if conf > 0.75 and character_count < 7:
            # print(element, conf)
            # 判断字符是否为中文
            if is_chinese_char(element):
                charatcter += element
                character_count += 1
        # 若置信度大于0.8，尝试提取数字标签
        if conf > 0.8:
            for i in element:
                if i.isdigit():
                    num_str += i
                else:
                    break
            # 若数字标签长度大于1，尝试转化为整数
            if (len(num_str) > 1):
                try:
                    lable_number = int(num_str)
                except ValueError as e:
                    lable_number = -1

    return [lable_number, charatcter]


def draw_bounding_box(image_path, errors_box, question_box, output_path):
    """在图像上绘制边界框并保存"""
    # 读取图像
    image = cv2.imread(image_path)
    # 绘制错误框（红色，厚度为20）
    for err in errors_box:
        x_center, y_center, width, height = err
        # 计算方框的左上角和右下角坐标
        x1 = int(x_center - width / 2)
        y1 = int(y_center - height / 2)
        x2 = int(x_center + width / 2)
        y2 = int(y_center + height / 2)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), thickness=20)

    # 绘制问题框（绿色，厚度为10）
    for question in question_box:
        x_center, y_center, width, height = question
        # 计算方框的左上角和右下角坐标
        x1 = int(x_center - width / 2)
        y1 = int(y_center - height / 2)
        x2 = int(x_center + width / 2)
        y2 = int(y_center + height / 2)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), thickness=10)

    cv2.imwrite(output_path, image)


def preProcess():
    """
   预处理函数，负责预测模型输出、过滤结果、整理坐标数据以及记录移除的ID。
   返回值:
   dict_coordinate_data (dict): 以文件名（不含后缀）为键，字典为值的字典。
   每个内部字典存储了ID与对应坐标数据（xywh形式）的映射。

   sorted_coordinate_dicts (dict): 以文件名（不含后缀）为键，有序坐标字典列表为值的字典。
   每个内部列表按横坐标升序排列，包含ID及其坐标数据。

   removed_id_dicts (dict): 以文件名（不含后缀）为键，移除的ID列表为值的字典。
    """
    # 初始化变量
    removed_id_dicts = dict()
    sorted_coordinate_dicts = dict()
    dict_coordinate_data = dict()
    results = model.predict(source=dir, save_crop=True, project='./runs/segment/')   # 调用模型预测，保存裁剪结果

    # 遍历目录结构，同步处理预测结果和文件名
    for root, dirs, files in os.walk(dir):
        for r, filename in zip(results, files):
            # 初始化当前文件相关的变量

            removed_id = []
            filename_without_suffix = filename.split('.')[-2]
            id_xlabel_dict = dict()
            # 遍历预测结果中的每个边界框
            for id, element in enumerate(r.boxes.xywh):
                # 判断宽度是否超出最大限制
                if (element[2] > max_width):
                    # 移除超限文件并记录移除的ID
                    filepath = seq_to_filepath(filename_without_suffix, id, result_dir)
                    print(id, element)
                    print(filepath)
                    os.remove(filepath)
                    removed_id.append(id)
                # 存储ID与坐标数据的映射
                id_xlabel_dict[id] = element.tolist()
            # 按横坐标升序排序坐标数据
            sorted_coordinate_dicts[filename_without_suffix] = sorted(
                id_xlabel_dict.items(), key=lambda x: x[1][0], reverse=False)
            # 将所有坐标数据存入字典
            dict_coordinate_data[filename_without_suffix] = id_xlabel_dict
            # 记录当前文件移除的ID
            removed_id_dicts[filename_without_suffix] = removed_id

    print('检查完毕...')
    return dict_coordinate_data, sorted_coordinate_dicts, removed_id_dicts


def wholeProcess():
    """
    整体处理流程，包括预处理、请求结果、检查结果、重绘图像等步骤。

    不返回任何值，但执行一系列操作并生成最终标注图像。
    """
    print('开始整体处理流程...')
    results_with_question = dict()  # 存储存在疑问的结果
    results_with_error = dict()  # 存储存在错误的结果
    all_book_result_in_dict = dict()  # 存储所有书籍识别结果
    # 清理旧的运行目录
    if os.path.exists('./runs'):
        shutil.rmtree('./runs')
    # 执行预处理步骤
    dict_coordinate_data, sorted_coordinate_dicts, removed_id_dicts = preProcess()

    # 请求并保存识别结果
    print('确认请求 ...')

    for name, sorted_dict in sorted_coordinate_dicts.items():
            all_book_result_in_list_dict = dict()  # 存储单个文件内所有书籍识别结果
            for key, xywh in sorted_dict:
                if key in removed_id_dicts[name]:  # 若ID已被移除，则跳过
                    continue
                path = seq_to_filepath(name, key, result_dir)   # 构建文件路径
                if os.path.exists(path):
                    all_book_result_in_list_dict[key] = send_post_request(
                        image_to_base64(path)
                    ).json()  # 发送请求并获取响应JSON  存储识别结果
                    # print('finish ' + str(key))
            all_book_result_in_dict[name] = all_book_result_in_list_dict  # 将单个文件的识别结果加入总结果字典

    # 从数据库获取书籍信息
    bookDao = BookDao()
    resultSet = bookDao.getBooks()
    bookDao.close()
    # 检查识别结果并分类
    for name, list_dict in all_book_result_in_dict.items():
        last_number = -1
        result_with_error = []  # 存储当前文件中存在错误的ID
        result_with_question = []  # 存储当前文件中存在疑问的ID

        for id, info in list_dict.items():
            this_number_str, character = getSingleBookResult(info)  # 提取单个书籍的编号和字符信息
            try:
                this_number = int(this_number_str)  # 尝试转换编号为整数
            except ValueError as e:
                this_number = -1  # 若转换失败，设置为-1
            
            this_number = findLabelFromName(resultSet, character)  # 从数据库中查找标签

            print(str(this_number), character)
            if this_number == -1:
                result_with_question.append(id)  # 若未找到标签，记录为疑问
                last_number = this_number
                continue
            elif last_number == -1:
                last_number = this_number
                continue
            elif this_number == last_number or this_number == last_number + 1:
                pass  # 连续编号或相邻编号，不做处理
            else:
                result_with_error.append(id)  # 编号不连续且非相邻，记录为错误

            # if label_number == -1:
            # 更新last_number
            last_number = this_number


        results_with_question[name] = result_with_question
        results_with_error[name] = result_with_error


    print('rewrite to the img')

    # 重绘图像，标记出存在疑问和错误的边界框
    for name in results_with_question.keys():
        err_boxes = [dict_coordinate_data[name][index] for index in results_with_error[name]]
        ques_boxes = [dict_coordinate_data[name][index] for index in results_with_question[name]]
        img_path = './img/{}.jpg'.format(name)
        output_path = './output/{}.jpg'.format(name)

        draw_bounding_box(img_path, err_boxes, ques_boxes, output_path)
    # 创建完成标志目录，并清理临时图像目录
    os.mkdir('finish.flag')
    shutil.rmtree('./img')
    return

def findBookProces(book_name):
    """
    查找特定书籍过程，类似于`wholeProcess()`，但专注于寻找与指定书名部分匹配的结果。

    参数:
    book_name (str): 待查找的书籍名称。

    不返回任何值，但执行一系列操作并生成最终标注图像。
    """
    print('开始书籍查找...')
    results_with_question = dict()  # 存储存在疑问的结果
    results_with_error = dict()  # 存储存在错误的结果
    results_with_right_name = dict()  # 存储与指定书名部分匹配的结果
    all_book_result_in_dict = dict()  # 存储所有书籍识别结果
    # 清理旧的运行目录
    if os.path.exists('./runs'):
        shutil.rmtree('./runs')
    # 执行预处理步骤
    dict_coordinate_data, sorted_coordinate_dicts, removed_id_dicts = preProcess()

    # 请求并保存识别结果
    print('确认请求 ...')

    for name, sorted_dict in sorted_coordinate_dicts.items():
            all_book_result_in_list_dict = dict()   # 存储单个文件内所有书籍识别结果
            for key, xywh in sorted_dict:
                if key in removed_id_dicts[name]:  # 若ID已被移除，则跳过
                    continue
                path = seq_to_filepath(name, key, result_dir)  # 构建文件路径
                if os.path.exists(path):
                    all_book_result_in_list_dict[key] = send_post_request(
                        image_to_base64(path)
                    ).json()  # 发送请求并获取响应JSON  存储识别结果
                    print('finish ' + str(key))
            all_book_result_in_dict[name] = all_book_result_in_list_dict  # 将单个文件的识别结果加入总结果字典

    # 从数据库获取书籍信息
    bookDao = BookDao()
    resultSet = bookDao.getBooks()
    bookDao.close()
    print('to find {}'.format(book_name))
    # 检查识别结果并分类
    for name, list_dict in all_book_result_in_dict.items():
        result_with_error = []  # 存储当前文件中存在错误的ID
        result_with_question = []  # 存储当前文件中存在疑问的ID
        result_with_right_name = []  # 存储当前文件中与指定书名部分匹配的ID

        for book_id, info in list_dict.items():
            this_number_str, character = getSingleBookResult(info)  # 提取单个书籍的编号和字符信息
            try:
                this_number = int(this_number_str)   # 尝试转换编号为整数
            except ValueError as e:
                this_number = -1  # 若转换失败，设置为-1
            
            this_number = findLabelFromName(resultSet, character)

            print(str(this_number), character)
            length = len(character)
            if length == 0:
                continue
            count = 0
            # 对于每个识别结果，计算其字符与待查找书名的相似度
            for i in book_name:
                if i in character:  # 如果书名中的字符存在于识别结果的字符中
                    count += 1  # 相似度计数器加1
                # 当相似度超过阈值（此处为50%）时，认为该识别结果与待查找书名部分匹配
                if count / length > 0.5:
                    result_with_right_name.append(book_id)  # 将匹配的ID添加到结果列表中

        # 将当前文件的疑问、错误及匹配结果分别添加到全局字典中
        results_with_question[name] = result_with_question
        results_with_error[name] = result_with_error
        results_with_right_name[name] = result_with_right_name


    print('重写进图片')

    # 遍历所有有疑问结果的文件，重新绘制标注图像
    for name in results_with_question.keys():
        # 仅使用与待查找书名部分匹配的边界框作为错误框
        err_boxes = [dict_coordinate_data[name][index] for index in results_with_right_name[name]]
        # 不绘制疑问框
        ques_boxes = []
        # 构建原图路径和输出路径
        img_path = './img/{}.jpg'.format(name)
        output_path = './output/{}.jpg'.format(name)
        # 调用`draw_bounding_box`函数绘制标注图像
        draw_bounding_box(img_path, err_boxes, ques_boxes, output_path)
    # 创建完成标志目录
    os.mkdir('finish.flag')
    # 删除临时图像目录
    shutil.rmtree('./img')
    return

def hsv_get(image_path):
    """
    再次分割书脊获得书标区域
    """
    # 读取图像
    image = cv2.imread(image_path)

    # 将图像转换为HSV颜色空间
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 定义红色的HSV范围
    lower_red = np.array([0, 100, 100])    # 红色的低阈值
    upper_red = np.array([10, 255, 255])   # 红色的高阈值

    # 创建一个mask，其中红色区域为白色，其他区域为黑色
    mask = cv2.inRange(hsv, lower_red, upper_red)

    # 寻找红线区域的轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 设置上下偏移量
    y_offset_top = -3
    y_offset_bottom = 17

    # 在原始图像上绘制红线区域的轮廓（仅作为示例）
    if contours:
        # 对轮廓按面积排序，取最大的两个轮廓
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]

        # 获取两条红线的 y 坐标
        y_coords = []
        for contour in contours:
            _, y, _, _ = cv2.boundingRect(contour)
            y_coords.append(y)

        # 确定上下两条红线的 y 坐标并应用偏移量
        y_coords.sort()
        y_top = max(y_coords[0] - y_offset_top, 0)
        y_bottom = min(y_coords[1] + y_offset_bottom, image.shape[0])

        # 提取两条红线之间的区域
        between_region = image[y_top:y_bottom, :]

        # 保存结果
        # cv2.imwrite('out/between_regions_hsv.jpg', between_region)
        shubiao = between_region

        print("两条最长红线之间的区域分割完成并保存")
    else:
        print("未找到红线区域，请调整阈值或检查图像")

if __name__ == '__main__':
    findBookProces(book_name)
    