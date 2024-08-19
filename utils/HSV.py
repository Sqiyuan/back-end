import cv2
import numpy as np

from utils.ImageExecute import image2base64, image_to_base64
from utils.OCR import send_post_request


def hsv_get(image):
    """
    再次分割书脊获得书标区域
    """

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
    y_offset_top = -15
    y_offset_bottom = 10

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
        return between_region
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
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
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

def rotate_image_to_horizontal(image):
    # 将图像转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 使用二值化处理
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # 使用 Canny 边缘检测
    edges = cv2.Canny(binary, 50, 150, apertureSize=3)
    
    # 查找轮廓
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 初始化旋转角度
    angle = 0
    for cnt in contours:
        # 获取最小外接矩形
        rect = cv2.minAreaRect(cnt)
        (x, y), (w, h), rect_angle = rect
        
        # 选择角度为小于 45 度的角度
        if w < h:
            rect_angle = 90 + rect_angle
        angle += rect_angle
    
    # 计算平均角度
    angle /= len(contours)
    print(angle)
    # 判断是否需要旋转
    if angle > 80:
        angle = 0
    else:
        angle = -90
    
    # 旋转图像至水平
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    # 计算旋转后的图像大小
    abs_cos = abs(M[0, 0])
    abs_sin = abs(M[0, 1])
    new_w = int(h * abs_sin + w * abs_cos)
    new_h = int(h * abs_cos + w * abs_sin)
    
    # Adjust the rotation matrix
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]
    rotated_image = cv2.warpAffine(image, M, (new_w, new_h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    return rotated_image

def getSingleCallNum(image_path):
    """
    识别并获取单本书的索书号（包括符号“=-:./”）
    返回ASCII码列表
    """
    # 读取分割后的索书号区域图像
    image = cv2.imread(image_path)
    #hsv分割
    hsv_image = hsv_get(image)
    if hsv_image.size == 0:
        return None
    rotate_image = rotate_image_to_horizontal(hsv_image)
    #图像处理
    pre_image = preprocess_image(rotate_image)
    #z转为base64
    base_64 = image2base64(pre_image)
    #OCR识别
    response = send_post_request(base_64).json()['data']['raw_out']
    # 创建列表用于保存有效的字符
    ascii_codes = []
    chars = []

    for _, element, conf in response:
        if conf > 0.8:
            
            # 拆分并检查每个字符是否有效
            for char in element:
                char = char.upper()#转为大写字母
                if char.isupper() or char.isdigit() or char in "=-:./":
                    chars.append(char)
    print("处理前：",chars)

    # 处理第一个字符
    if chars and not chars[0].isalpha():
        # 找到与第一个字符最相似的字母
        most_similar_char = find_most_similar_char(chars[0])
        if most_similar_char is not None:
            chars[0] = most_similar_char
            print("处理后：",chars)
    # 将有效字符转换为ASCII码并添加到列表中
    ascii_codes.extend(ord(c) for c in chars)
    return ascii_codes

def find_most_similar_char(char):
    """
    寻找与给定字符最相似的大写字母
    """
    # 假设的相似度阈值
    similarity_threshold = 0.5
    # 假设的字母相似度字典
    similarity_dict = {
        '0': ('O', 0.9),
        '1': ('I', 0.8),
        '2': ('Z', 0.7),
        # 其他字符及其相似度
    }

    # 查找相似度最高的字母
    max_similarity = 0
    most_similar_char = None
    for digit, (letter, similarity) in similarity_dict.items():
        if char == digit and similarity > max_similarity and similarity > similarity_threshold:
            max_similarity = similarity
            most_similar_char = letter

    return most_similar_char