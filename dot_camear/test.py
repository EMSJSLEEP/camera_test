import cv2
import numpy as np
def detect_lines(image):
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(image, 120, 160, apertureSize=5)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 120)
    cv2.imshow('Detected Lines', edges)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return lines

def find_adjacent_lines(lines):
    lines = [line[0] for line in lines]
    candidates = []
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            theta_i = lines[i][1]
            theta_j = lines[j][1]
            angle = abs(theta_i - theta_j)
            if 80 <= angle <= 100:
                candidates.append((lines[i], lines[j]))
    return candidates

def find_parallel_lines(image, line1, line2):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape
    lines = [line1, line2]
    # Initialize the parallel lines at the estimated position
    for line in lines:
        rho, theta = line
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return image

def find_optimal_parallel_lines(image, line1, line2):
    best_diff = float('inf')
    best_l1, best_l2 = None, None
    for offset in range(-7, 8):
        l1 = line1 + offset
        l2 = line2 + offset
        # Compute pixel differences
        diff = compute_pixel_difference(image, l1, l2)
        if diff < best_diff:
            best_diff = diff
            best_l1, best_l2 = l1, l2
    return best_l1, best_l2

def compute_pixel_difference(image, line1, line2):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape
    # Compute the pixel difference between the lines
    # This is a placeholder function. Implement the pixel comparison logic here.
    return np.abs(np.mean(gray[int(line1):int(line1+10), :]) - np.mean(gray[int(line2):int(line2+10), :]))



# 读取点状DataMatrix二维码图像
image = cv2.imread('datamatrix3.jpg', cv2.COLOR_BGR2GRAY)

# 反转图像颜色，适应黑底白点图像
# image = cv2.bitwise_not(image)

# 步骤S1：开运算（消除细小杂点）
kernel = np.ones((2, 2), np.uint8)
opened_image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
close_image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
# # 步骤S2：拉普拉斯增强
# laplacian_kernel = np.array([[0, 1, 0], 
#                              [1, -6, 1], 
#                              [0, 1, 0]])

# # 应用卷积计算变种拉普拉斯结果
# enhanced_image = cv2.filter2D(opened_image, cv2.CV_64F, laplacian_kernel)
# enhanced_image = cv2.convertScaleAbs(enhanced_image)

# 增加对比度
# alpha = 1.2  # 对比度控制 (1.0-3.0之间)
# beta = 0   # 亮度控制 (0-100之间)
# enhanced_image = cv2.convertScaleAbs(enhanced_image, alpha=alpha, beta=beta)

# 步骤S3：根据二维码的底色进行腐蚀或膨胀
# 假设此处为白底黑码，进行腐蚀操作
# processed_image = cv2.erode(enhanced_image, kernel, iterations=1)

# 如果是黑底白码，使用膨胀操作
# processed_image = cv2.dilate(enhanced_image, kernel, iterations=1)

# 步骤S4：高斯滤波平滑处理
ret, thresh = cv2.threshold(close_image, 150, 255, cv2.THRESH_BINARY)
smoothed_image = cv2.GaussianBlur(thresh, (9, 9), 0)





# lines = detect_lines(smoothed_image)

# # Find adjacent lines
# candidates = find_adjacent_lines(lines)

# # Process each candidate
# for line1, line2 in candidates:
#     image = find_parallel_lines(image, line1, line2)
#     line1_opt, line2_opt = find_optimal_parallel_lines(image, line1, line2)

# # Display the image
# cv2.imshow('Detected Lines', image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# 步骤S5：DataMatrix二维码定位和识别
# 使用 dmtx 解码库（确保已安装：pip install pylibdmtx）
from pylibdmtx import pylibdmtx

decoded_objects = pylibdmtx.decode(thresh)
# cv2.imwrite("new2.png", thresh)
# 打印解码结果
print(decoded_objects)
    
# 显示处理后的图像
cv2.imshow('Original Image', image)
cv2.imshow('Opened Image', opened_image)
# cv2.imshow('Enhanced Image', enhanced_image)
# cv2.imshow('Processed Image', processed_image)
cv2.imshow('Smoothed Image', smoothed_image)
cv2.imshow('thresh Image', thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()
