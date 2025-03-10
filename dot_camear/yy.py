from pyzbar.pyzbar import decode
from PIL import Image
import numpy as np
import cv2

def decode_datamatrix(image_path):
    # 读取图像
    threshold = 180
    img0 = cv2.imread("datamatrix.jpeg", cv2.IMREAD_GRAYSCALE)

    # 反转图像颜色，适应黑底白点图像
    # img0 = cv2.bitwise_not(img0)

    kernel = np.ones((7, 7), np.uint8)
    opened_image = cv2.morphologyEx(img0, cv2.MORPH_OPEN, kernel)
    # 高斯模糊
    gauss = cv2.GaussianBlur(img0, (5, 5), 0)

    # 二值化处理
    ret, thresh = cv2.threshold(gauss, threshold, 255, cv2.THRESH_BINARY)
    decoded_objects = decode(thresh)

    # 创建二值化数组
    binary_array = np.zeros((18, 18), dtype=np.uint8)
    
    for obj in decoded_objects:
        points = obj.polygon
        if len(points) == 4:
            for i in range(len(points)):
                x1, y1 = points[i]
                x2, y2 = points[(i + 1) % 4]
                cv2.line(binary_array, (x1, y1), (x2, y2), 1, 1)
    
    return binary_array

print(decode_datamatrix("datamatrix.jpeg"))
