import base64
from dao.BaseDao import BaseDao
import cv2
from PIL import Image
import io

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

def image2base64(image):
    """
    将图像转换为base64编码字符串
    """
    # 使用PIL加载图像
    img = Image.fromarray(image)
    # 创建一个BytesIO对象来保存图像数据
    buffer = io.BytesIO()
    # 将图像保存到BytesIO对象中
    img.save(buffer, format='JPEG')
    # 获取BytesIO对象中的二进制数据
    img_bytes = buffer.getvalue()
    # 将二进制数据转换为base64编码字符串
    base64_str = base64.b64encode(img_bytes).decode('utf-8')
    return base64_str

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

if __name__ == '__main__':
    print(image_to_base64('shuji.jpg'))
