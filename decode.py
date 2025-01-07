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
        # print(max_ratio)
        start_time = time.time()
        gray_image = cv2.cvtColor(_image, cv2.COLOR_BGR2GRAY)
        denoised_image = cv2.fastNlMeansDenoising(_image, None)
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
            self.save_picture(resized_image, i)
            decoded_data = self.simple_decode_dmtx(resized_image, piece_time * (i + 1) * (i + 1))
            if decoded_data:
                return decoded_data

    def simple_decode_dmtx(self, image, timeout_ms):
        all_barcode_info = pylibdmtx.decode(image, timeout=int(timeout_ms), max_count=1000)
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

        # #创建一个保存图像的目录
        output_dir = "./debug_images"
        os.makedirs(output_dir, exist_ok=True)

        def save_image(step, img):
            """保存每一步处理的图像"""
            path = os.path.join(output_dir, f"step_{step}.jpg")
            cv2.imwrite(path, img)
            print(f"Saved: {path}")

        # 开操作去除细丝以及杂点
        kernel = np.ones((3, 3), np.uint8)
        open_image_2 = cv2.morphologyEx(_image, cv2.MORPH_OPEN, kernel, iterations=1)
        save_image("7_open", open_image_2)

        # # 闭操作填充二维码空隙
        kernel2 = np.ones((3, 3), np.uint8)
        close_image_2 = cv2.morphologyEx(open_image_2, cv2.MORPH_CLOSE, kernel2, iterations=1)
        save_image("8_close", close_image_2)
    
        gaussian_blur_image = cv2.GaussianBlur(close_image_2, (3, 3), 1)
        save_image("10_gaussian_blur", gaussian_blur_image)

        dst_image = cv2.resize(gaussian_blur_image, (200, 200))
        save_image("11_resized", dst_image)

        flag = self.simple_decode_dmtx(dst_image, timeout_ms)
        elapsed_time = (time.time() - start_time) * 1000  # 转为毫秒
        print(f"Cost {elapsed_time:.2f}ms for processing image")
        return flag

    def save_picture(self, img, step):
        # #创建一个保存图像的目录
        output_dir = "./debug_images"
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"step_{step}.jpg")
        cv2.imwrite(path, img)
        print(f"Saved: {path}")

    def Mean_Filtering(self, img):
        #特点：通过计算局部区域的像素均值，平滑图像并减少噪声。
        #适用场景：用于去除高频噪声（如随机噪声）并使图像更加平滑。
        kernel = np.ones((3, 3), np.float32) / 9
        smoothed = cv2.filter2D(img, -1, kernel)
        return smoothed
    
    def Gaussian_Blur(self, img):
        #特点：利用高斯函数分布对像素进行加权平滑，减少噪声。
        #适用场景：适用于高斯分布的噪声（如环境噪声）或在二值化前用于平滑图像。
        smoothed = cv2.GaussianBlur(img, (25, 25), 4)
        return smoothed
    
    def Median_Filtering(self, img):
        #特点：对局部区域的像素值取中值，去除噪声。
        #适用场景：对椒盐噪声（Salt-and-Pepper Noise）非常有效。
        
        smoothed = cv2.medianBlur(img, 3)
        return smoothed
    
    def Bilateral_Filtering(self, img):
        #特点：在去噪的同时保持边缘的锐利。
        #适用场景：处理有明显边缘结构的图像，避免模糊化边缘。
        smoothed = cv2.bilateralFilter(img, 5, 75, 75)
        return smoothed
    
    def Adaptive_Thresholding(self, img):
        #特点：根据图像局部区域的特性动态计算阈值，适合光照不均的图像。
        #适用场景：用于二值化前处理或直接进行二值化。
        thresholded = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY, 11, 2)
        return thresholded
    
    def Edge_Detection_Filters(self, img):
        #特点：用于强调图像边缘，便于后续处理。
        #适用场景：提取二值化后的边缘信息。
        edges = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
        edges = cv2.Canny(image, 50, 150)


if __name__ == "__main__":
    x = Decode()
    image_path = "./10.png"
    src_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    src_image = cv2.resize(src_image, (150, 150))
    x.save_picture(src_image, "1")
    src_image = cv2.fastNlMeansDenoising(src_image, None)
    x.save_picture(src_image, "2")
    normalized_image = cv2.normalize(src_image, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    x.save_picture(normalized_image, "3")

    # width, height = src_image.shape[1], src_image.shape[0]
    # src_image = cv2.flip(src_image, 0)
    # src_image = cv2.resize(src_image, (100, 100))
    kernel = np.ones((3, 3), np.uint8)
    open_image_2 = cv2.morphologyEx(normalized_image, cv2.MORPH_OPEN, kernel, iterations=1)
    x.save_picture(open_image_2, "open")
    # kernel2 = np.ones((3, 3), np.uint8)
    # src_image = x.Gaussian_Blur(src_image)
    # src_image = x.Bilateral_Filtering(src_image)
    # x.save_picture(src_image, "step_resize")

    #黑白二值化
    # src_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    # _, binary_image = cv2.threshold(src_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if src_image is None:
        print("Failed to load image. Check the file path.")
    else:
        # result = x.decode_ecc200(src_image, timeout_ms=6000)
        result = x.simple_decode_dmtx(open_image_2, timeout_ms=6000)
        # result = x.decode_dot(src_image, timeout_ms=6000)
        print(result)