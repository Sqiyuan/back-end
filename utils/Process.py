import os
import shutil
from ultralytics import YOLO
from utils.ImageExecute import *
from utils.HSV import *
from utils.OCR import *
from utils.Pic_pre import *

dir = './img/'
pre_dir = './img/pre/'  # 待处理图像目录
result_dir = './runs/segment/predict/crops/book/'   # 预测结果保存目录
max_width = 400 # 图像最大宽度限制
book_name = '开始写吧'
model = YOLO('./ex_best.pt')    # 实例化YOLO模型，加载预训练权重

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
    # 清理旧的运行目录
    if os.path.exists('./runs'):
        shutil.rmtree('./runs')
    if os.path.exists('./hsv'):
        shutil.rmtree('./hsv')
    if not os.path.exists('./hsv'):
        os.mkdir('./hsv')
    #预处理图片
    # process_folder_images(pre_dir)
    print('预处理...')
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
    """整体处理流程，包括预处理、请求结果、检查结果、重绘图像等步骤。"""
    print('开始整体处理流程...')
    results_with_question = dict()  # 存储存在疑问的结果
    results_with_error = dict()  # 存储存在错误的结果
    all_book_result_in_dict = dict()  # 存储所有书籍识别结果
    
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
                    all_book_result_in_list_dict[key] = getSingleCallNum(path)

            all_book_result_in_dict[name] = all_book_result_in_list_dict  # 将单个文件的识别结果加入总结果字典

    # 从数据库获取书籍信息
    bookDao = BookDao()
    resultSet = bookDao.getBooks()
    bookDao.close()
    # 检查识别结果并分类
    for name, list_dict in all_book_result_in_dict.items():
        result_with_error = []
        ascii_results = []

        # 遍历字典中的键值对并存储 ASCII 码结果
        for id, ascii in list_dict.items():
            if ascii is not None:
                # 获取当前书的 ASCII 码结果
                ascii_results.append((id, ascii))
            else:
                # 如果 data 不存在，继续下一项
                continue

        # 循环结束后，依次比较相邻书籍的 ASCII 码顺序
        for i in range(1, len(ascii_results)):
            prev_id, prev_ascii = ascii_results[i - 1]
            current_id, current_ascii = ascii_results[i]

            # 检查是否有顺序错位
            if any(current < prev for current, prev in zip(current_ascii, prev_ascii)):
                result_with_error.append(current_id)
            elif i < len(ascii_results) - 1:
                _, next_ascii = ascii_results[i + 1]
                if any(current > next for current, next in zip(current_ascii, next_ascii)):
                    result_with_error.append(current_id)
                    results_with_error[name] = result_with_error
    print('rewrite to the img')

    # 重绘图像，标记出存在疑问和错误的边界框
    for name in results_with_error.keys():
        err_boxes = [dict_coordinate_data[name][index] for index in results_with_error[name]]
        # ques_boxes = [dict_coordinate_data[name][index] for index in results_with_question[name]]
        img_path = './img/{}.jpg'.format(name)
        output_path = './output/{}.jpg'.format(name)

        draw_bounding_box(img_path, err_boxes, err_boxes, output_path)
    # 创建完成标志目录，并清理临时图像目录
    os.mkdir('finish.flag')
    # shutil.rmtree('./img')
    return

def findBookProces(book_name):
    """查找特定书籍过程"""
    print('开始书籍查找...')
    results_with_question = dict()  # 存储存在疑问的结果
    results_with_error = dict()  # 存储存在错误的结果
    results_with_right_name = dict()  # 存储与指定书名部分匹配的结果
    all_book_result_in_dict = dict()  # 存储所有书籍识别结果

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

            if is_subsequence(character, book_name):
                result_with_right_name.append(book_id)

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
    # shutil.rmtree('./img')
    return