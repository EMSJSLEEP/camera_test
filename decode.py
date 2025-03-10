# -*-coding:utf-8 -*-
import time
import cv2
import os
import math
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
        start_time = time.time()
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
            #self.save_picture(resized_image, i)
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
    
    def decode_dot(self, _image, kernel_size, timeout_ms=3000):
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
        #save_image("7_open", open_image_2)

        # 闭操作填充二维码空隙
        kernel2 = np.ones((kernel_size, kernel_size), np.uint8)
        close_image_2 = cv2.morphologyEx(open_image_2, cv2.MORPH_CLOSE, kernel2, iterations=1)
        #save_image("8_close", close_image_2)
    
        gaussian_blur_image = cv2.GaussianBlur(close_image_2, (3, 3), 1)
        #save_image("9_gaussian_blur", gaussian_blur_image)

        flag = self.simple_decode_dmtx(gaussian_blur_image, timeout_ms)

        if flag == None:
            if kernel_size == 7:
                kernel_size = 5
                kernel = np.ones((3, 3), np.uint8)
                open_image_2 = cv2.morphologyEx(_image, cv2.MORPH_OPEN, kernel, iterations=2)
            elif kernel_size == 3:
                kernel_size = 5
            #save_image("10_open", open_image_2)
            kernel2 = np.ones((kernel_size, kernel_size), np.uint8)
            close_image_2 = cv2.morphologyEx(open_image_2, cv2.MORPH_CLOSE, kernel2, iterations=1)
            #save_image("12_close", close_image_2)
        
            gaussian_blur_image = cv2.GaussianBlur(close_image_2, (3, 3), 1)
            #save_image("13_gaussian_blur", gaussian_blur_image)

            flag = self.simple_decode_dmtx(gaussian_blur_image, timeout_ms)
        elapsed_time = (time.time() - start_time) * 1000 
        print(f"Cost {elapsed_time:.2f}ms for processing image")
        return flag

    def auto_decode(self, _image, timeout_ms=3000):
        decode_result = None
        src_image = cv2.fastNlMeansDenoising(_image, None)
        normalized_image = self.is_normalize_deal(src_image)
        kernel_size, deal_image = self.hough_circle_detection(normalized_image)
        print("kernel size is ", kernel_size)
        if kernel_size == 0:
            decode_result = self.decode_ecc200(deal_image, timeout_ms)
        else:
            decode_result = self.decode_dot(deal_image, kernel_size, timeout_ms)
        return decode_result

    def save_picture(self, img, step):
        # #创建一个保存图像的目录
        output_dir = "./debug_images"
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"step_{step}.jpg")
        cv2.imwrite(path, img)
        print(f"Saved: {path}")

    def Mean_Filtering(self, img):
        # 均值滤波以减少噪声
        # gray_image = cv2.blur(src_image, (9,9))
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
        edges = cv2.Canny(img, 50, 150)

    def dynamic_kernel_morphology(self, normalized_image):
        # 检测轮廓
        contours, _ = cv2.findContours(normalized_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
        filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 50]
        cv2.drawContours(contours_image, filtered_contours, -1, (0, 255, 0), 2)

        # 计算点的宽度
        sizes = [cv2.boundingRect(cnt)[2] for cnt in contours if cv2.contourArea(cnt) > 5]
        print(sizes)
        # 动态核大小
        average_size = int(np.mean(sizes)) if sizes else 3
        kernel_size = min(3, average_size)  # 核的最小大小为3
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        # 形态学开运算
        open_image_2 = cv2.morphologyEx(normalized_image, cv2.MORPH_OPEN, kernel, iterations=1)
        close_image_2 = cv2.morphologyEx(open_image_2, cv2.MORPH_CLOSE, kernel, iterations=1)
        cv2.imshow("Contours", contours_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return close_image_2

    def hough_circle_detection(self, _image):
        resize_image = cv2.resize(_image, (200, 200))
        circles = cv2.HoughCircles(
            resize_image,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=18,       # 设置最小圆心距离
            param1=10,        # Canny 边缘检测的高阈值
            param2=12,        # 圆心检测的阈值
            minRadius=1,     # 最小半径
            maxRadius=6     # 最大半径normalized_image
        )
        total_area = 0
        circle_count = 0
        kernel_calculation = 0
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                x, y, r = i[0], i[1], i[2]
                area = math.pi * (r ** 2)
                total_area += area
                circle_count += 1
                # cv2.circle(normalize_image, (x, y), r, (0, 255, 0), 2)
                # cv2.circle(normalize_image, (x, y), 2, (0, 0, 255), 3)
            print(f"There find {circle_count} circles")

            if circle_count >= 12:
                average_area = total_area / circle_count
                print(average_area)
                kernel_calculation = self.map_to_odd_range(average_area)
            return kernel_calculation, resize_image
        else:
            return 0, _image
        

    def is_normalize_deal(self, _image):
        avg_brightness = np.mean(_image)
        print(f"avg brightness is {avg_brightness}")
        if avg_brightness <= 90:
            normalize_image = cv2.normalize(_image, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
            return normalize_image
        else:
            return _image

    def map_to_odd_range(self, value):
        sqrt_value = math.sqrt(value)

        odd_numbers = [3, 5, 7]
    
        closest_odd = min(odd_numbers, key=lambda x: abs(x - sqrt_value))
        
        return closest_odd
        



if __name__ == "__main__":
    x = Decode()
    for i in range(1, 12):
        image_path = f"dot{i}.png"
        print(image_path + "\n")
        img= cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if image_path == "dot1.png":
            mirror_img = cv2.flip(img, 1)
            print(x.auto_decode(mirror_img, 8000))
        else:
            print(x.auto_decode(img, 8000))
