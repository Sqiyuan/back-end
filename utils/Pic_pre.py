import os
import cv2
import numpy as np
import albumentations as A
from ultralytics import YOLO


# 图像质量改善 - 去噪与对比度调整
def improve_image_quality(image):
    denoised_img = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    lab = cv2.cvtColor(denoised_img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return enhanced_img


# 背景去除或减淡 - 阈值处理示例
def remove_background(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY)
    background_removed = cv2.bitwise_and(image, image, mask=thresh)
    return background_removed


# 预处理函数 - 使文字更清晰
def enhance_text(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    l = cv2.filter2D(l, -1, kernel)
    enhanced_img = cv2.merge((l, a, b))
    enhanced_img = cv2.cvtColor(enhanced_img, cv2.COLOR_LAB2BGR)
    return enhanced_img

# 数据增强 - 使用albumentations
def augment_data(image):
    transform = A.Compose([
        A.RandomBrightnessContrast(p=0.2),
        A.ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.1, rotate_limit=0, p=0.5),
    ])
    augmented = transform(image=image)['image']
    return augmented


def process_image(image_path):
    original_img = cv2.imread(image_path)

    # 检查图像是否为空
    if original_img is None:
        print(f"无法打开文件: {image_path}")
        return

    # 确保图像为彩色
    if len(original_img.shape) != 3 or original_img.shape[2] not in [3, 4]:
        print(f"图像 {image_path} 不是彩色图像")
        return
    
    # 改善图像质量
    improved_img = improve_image_quality(original_img)

    # 预处理使文字清晰
    text_enhanced_img = enhance_text(improved_img)

    # 背景去除
    background_removed = remove_background(text_enhanced_img)

    # 数据增强
    # augmented_img = augment_data(background_removed)

    # 保存带颜色信息的图像
    output_image_path = os.path.join('./img/pre', os.path.basename(image_path))
    cv2.imwrite(output_image_path, background_removed)

    print(f'处理好的图像已保存至: {output_image_path}')


def process_folder_images(folder_path):
    """处理文件夹中的所有图像"""
    for image_name in os.listdir(folder_path):
        if image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, image_name)
            process_image(image_path)


if __name__ == "__main__":
    image_path = './img/'  # 替换为你的图像路径
    # process_folder_images(image_path)
    model = YOLO('./ex_best.pt')
    results = model.predict(source="./img/", save_crop=True, save=True, project='./hsv/')
    print(f"打印result:{results}")
