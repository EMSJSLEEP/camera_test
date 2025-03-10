# -*-coding:utf-8 -*-
import time
import cv2
import os
import numpy as np
from pylibdmtx import pylibdmtx


class Decode(object):
    def __init__(self, path='image.jpg'):
        self.path = path
        self.qr_decoder = cv2.QRCodeDetector()
        
    def decode_ecc200_local(self):
        image = cv2.imread(self.path)
        all_barcode_info = pylibdmtx.decode(image, timeout=3000, max_count=100)
        if all_barcode_info != []:
            return all_barcode_info[0].data.decode("utf-8")
        else:
            return 'decode_fail'
    
    def decode_ecc200(self, _image, timeout_ms=3000):
        height, width = _image.shape[:2]
        if height < 80:
            max_ratio = 4
        elif height < 160:
            max_ratio = 3
        elif height < 320:
            max_ratio = 2
        else:
            max_ratio = 1
        print(max_ratio)
        start_time = time.time()
        gray_image = cv2.cvtColor(_image, cv2.COLOR_BGR2GRAY)
        denoised_image = cv2.fastNlMeansDenoising(gray_image, None)
        preprocess_time_ms = (time.time() - start_time) * 1000
        print(f"Preprocess time: {preprocess_time_ms:.2f} ms")
        left_time_ms = max(timeout_ms - preprocess_time_ms, 0)
        if left_time_ms <= 0:
            print("(cyg663) decode fail: Preprocess image for too long, no enough time for decode so just skip")
            return 'decode_fail'
        piece_total = sum((i * i) for i in range(1, max_ratio + 1))
        piece_time = left_time_ms / piece_total

        for i in range(max_ratio):
            resized_image = cv2.resize(denoised_image, 
                                       (int(width * (i + 1)), int(height * (i + 1))),
                                       interpolation=cv2.INTER_LINEAR)
            decoded_data = self.simple_decode_dmtx(resized_image, piece_time * (i + 1) * (i + 1))
            if decoded_data:
                return decoded_data

    def simple_decode_dmtx(self, image, timeout_ms):
        all_barcode_info = pylibdmtx.decode(image, timeout=int(timeout_ms), max_count=100)
        if all_barcode_info:
            return all_barcode_info[0].data.decode("utf-8")
        else:
            return None
        
    def decode_qr(self, _image):
        retval, decoded_info, points, straight_qrcode = self.qr_decoder.detectAndDecodeMulti(_image)
        if retval == False:
            return "decode_fail"
        else:
            return decoded_info
    
    def decode_dot(self, _image, timeout_ms):
        start_time = time.time()

        # 创建一个保存图像的目录
        # output_dir = "./debug_images"
        # os.makedirs(output_dir, exist_ok=True)

        # def save_image(step, img):
        #     """保存每一步处理的图像"""
        #     path = os.path.join(output_dir, f"step_{step}.jpg")
        #     cv2.imwrite(path, img)
        #     print(f"Saved: {path}")

        # 开操作去除细丝以及杂点
        open_image_2 = cv2.morphologyEx(_image, cv2.MORPH_OPEN, None, iterations=1)
        # save_image("7_open", open_image_2)

        # # 闭操作填充二维码空隙
        close_image_2 = cv2.morphologyEx(open_image_2, cv2.MORPH_CLOSE, None, iterations=2)
        # save_image("8_close", close_image_2)

        gaussian_blur_image = cv2.GaussianBlur(close_image_2, (5, 5), 0)
        # save_image("9_gaussian_blur", gaussian_blur_image)

        dst_image = cv2.resize(gaussian_blur_image, (110, 110))
        # save_image("10_resized", dst_image)

        flag = self.simple_decode_dmtx(dst_image, timeout_ms)
        elapsed_time = (time.time() - start_time) * 1000  # 转为毫秒
        print(f"Cost {elapsed_time:.2f}ms for processing image")
        return flag

if __name__ == "__main__":
    x = Decode()
    image_path = "./1.jpg"  # 替换为本地图片路径
    src_image = cv2.imread(image_path)

    if src_image is None:
        print("Failed to load image. Check the file path.")
    else:
        result = x.decode_dot(src_image, timeout_ms=6000)
        print(result)