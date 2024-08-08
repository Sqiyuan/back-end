import requests


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
        # print("docker识别结果:", response.text)
        return response
    except Exception as e:
        print("Error:", e)

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

def is_subsequence(a, b):
    """判断b是否是a的子序列"""
    sub_iter = iter(a)
    return all(char in sub_iter for char in b)
