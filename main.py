import requests
import re
import cv2
import numpy as np
from PIL import Image
from io import BytesIO

# ----------------------
# 一、调用OCR服务（trwebocr）
# ----------------------

def ocr_image(image_path):
    url = 'http://127.0.0.1:8080/api/tr-run/'
    with open(image_path, 'rb') as f:
        files = {'file': f}
        resp = requests.post(url, files=files)
        raw_out = resp.json().get("data", {}).get("raw_out", [])

    callnums = []
    for item in raw_out:
        box_info, text, conf = item
        if not isinstance(text, str) or not text.strip():
            continue
        text = text.strip()
        if is_call_number(text):
            cx, cy, w, h, angle = box_info
            callnums.append({"text": text, "cx": cx, "cy": cy})
    return callnums


# ----------------------
# 二、判断是否是索书号
# ----------------------

def is_call_number(text):
    # 简单判断是否像索书号（数字+点+大写字母）
    return re.match(r"^[A-Z]{1,3}\d{1,3}(\.\d+)?([\/=:\-\.A-Z0-9]+)?$", text)

# ----------------------
# 三、排序坐标（上到下，再左到右）
# ----------------------

def sort_by_position(callnums, y_thresh=30):
    # 先按行（cy）聚类，再每行内按cx排序
    sorted_items = sorted(callnums, key=lambda x: (x['cy']//y_thresh, x['cx']))
    return [item['text'] for item in sorted_items]

# ----------------------
# 四、将索书号标准化为可比大小
# ----------------------

def normalize_callnum(callnum):
    # 将索书号拆成 字母 + 数字 + 小数 + 后缀
    match = re.match(r"^([A-Z]+)(\d+)(?:\.(\d+))?(.*)$", callnum)
    if not match:
        return (callnum, )
    letter, num, decimal, rest = match.groups()
    return (letter, int(num), int(decimal) if decimal else 0, rest)

# ----------------------
# 五、检测是否错位
# ----------------------

def detect_misplaced(callnums_sorted):
    prev = None
    for i, cn in enumerate(callnums_sorted):
        now = normalize_callnum(cn)
        if prev and now < prev:
            print(f"第{i+1}本索书号【{cn}】排在了前一本【{callnums_sorted[i-1]}】之前，可能错位")
        prev = now


# ----------------------
# 六、主程序
# ----------------------

def main():
    image_path = 'E:/GraduationDesign/project/books/4.jpg'  # 替换成你的图像路径
    callnum_results = ocr_image(image_path)
    if not callnum_results:
        print("未识别到有效索书号")
        return

    callnum_sorted = sort_by_position(callnum_results)
    print("识别到的索书号顺序：")
    for i, cn in enumerate(callnum_sorted):
        print(f"{i+1}. {cn}")
    print("\n检测错位结果：")
    detect_misplaced(callnum_sorted)

if __name__ == '__main__':
    main()
