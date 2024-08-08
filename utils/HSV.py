import cv2
import numpy as np

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

        #分割图片路径获得图片名称
        lujing = image_path.split('/')
        name = lujing[len(lujing)-1]

        # 保存结果
        cv2.imwrite('./hsv/' + name, between_region)
        # shubiao = between_region

        # print("两条最长红线之间的区域分割完成并保存")
        return './hsv/' + name
    else:
        print("未找到红线区域，请调整阈值或检查图像")
        return 0
    
def getSingleCallNum(image_path):
    """
    得到单本书的索书号
    """
    return 0