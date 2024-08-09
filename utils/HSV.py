import cv2
import numpy as np

from utils.ImageExecute import image_to_base64
# from utils.OCR import send_post_request
# from utils.ImageExecute import image_to_base64

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
    y_offset_top = -22
    y_offset_bottom = 3

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

        #分割图片路径获得图片名称
        lujing = image_path.split('/')
        name = lujing[len(lujing)-1]

        # 保存结果
        cv2.imwrite('./hsv/' + name, between_region)
        # shubiao = between_region

        # print("两条最长红线之间的区域分割完成并保存")
        print('./hsv/' + name)
        return './hsv/' + name
    else:
        print("未找到红线区域，请调整阈值或检查图像")
        return 0
    
def preprocess_image(image):
    """
    对图像进行预处理，包括对比度增强、二值化和去噪。
    """
    # 增强对比度
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    image = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    # 转为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 二值化
    _, binary_image = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 去噪
    denoised_image = cv2.fastNlMeansDenoising(binary_image, None, 30, 7, 21)

    return denoised_image

def getSingleCallNum(image_path):
    """
    识别并获取单本书的索书号（多行文本，包括符号“=-:./”）
    """
    # 读取分割后的索书号区域图像
    image = cv2.imread(image_path)

    # 对图像进行预处理
    preprocessed_image = preprocess_image(image)
    print("pre_image",preprocessed_image)
    base_64 = image_to_base64(image_path)
    print("base64:", base_64)

    # 使用Tesseract进行字符识别，配置为多行文本识别模式
    config = '--psm 6'  # 允许文本有多个段落
    recognized_text = pytesseract.image_to_string(gray, config=config)

    # 包含大写字母、数字和指定符号的有效字符集合
    valid_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789=-:./")

    # 初始化空列表存储每行的有效索书号字符
    call_number_lines = []

    # 按行分割识别到的文本，并逐行处理
    for line in recognized_text.splitlines():
        # 筛选出每行中的有效字符
        filtered_line = ''.join([char for char in line if char in valid_chars])
        if filtered_line:
            call_number_lines.append(filtered_line)

    # 返回一个包含所有行有效字符的列表
    return call_number_lines

if __name__ == '__main__':
    image_path = './shuji.jpg'
    call_Num = getSingleCallNum(hsv_get(image_path))
    print("识别的索书号：", call_Num)