import cv2
import numpy as np
from pylibdmtx import pylibdmtx


# 读取点状DataMatrix二维码图像
image = cv2.imread('datamatrix3.jpg', cv2.IMREAD_GRAYSCALE)

# 反转图像颜色，适应黑底白点图像
image = cv2.bitwise_not(image)

# 步骤S1：开运算（消除细小杂点）
kernel = np.ones((2, 2), np.uint8)
opened_image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

# 步骤S2：拉普拉斯增强
laplacian_kernel = np.array([[0, 1, 0], 
                             [1, -6, 1], 
                             [0, 1, 0]])

# 应用卷积计算变种拉普拉斯结果
enhanced_image = cv2.filter2D(opened_image, cv2.CV_64F, laplacian_kernel)
enhanced_image = cv2.convertScaleAbs(enhanced_image)

# 增加对比度
alpha = 1.2  # 对比度控制 (1.0-3.0之间)
beta = 0   # 亮度控制 (0-100之间)
enhanced_image = cv2.convertScaleAbs(enhanced_image, alpha=alpha, beta=beta)

# 步骤S3：根据二维码的底色进行腐蚀或膨胀
# 假设此处为白底黑码，进行腐蚀操作
processed_image = cv2.erode(enhanced_image, kernel, iterations=1)

# 如果是黑底白码，使用膨胀操作
# processed_image = cv2.dilate(enhanced_image, kernel, iterations=1)

# 步骤S4：高斯滤波平滑处理
smoothed_image = cv2.GaussianBlur(processed_image, (5, 5), 0)

ret, thresh = cv2.threshold(smoothed_image, 150, 255, cv2.THRESH_BINARY)




# 步骤S3：直线检测 (Hough变换)
edges = cv2.Canny(thresh, 100, 150, apertureSize=3)

# 显示或保存边缘检测结果，帮助调试
# cv2.imshow('Edges', edges)

# 调整阈值参数，尝试不同的值（如100、150、50等）
lines = cv2.HoughLines(edges, 1, np.pi / 180, 50)
# print(lines)
# 检查是否检测到直线
if lines is None:
    print("未检测到任何直线。请尝试调整阈值或检查边缘检测结果。")
else:
    candidate_regions = []
    for i, line1 in enumerate(lines):
        for j, line2 in enumerate(lines[i + 1:]):
            rho1, theta1 = line1[0]
            rho2, theta2 = line2[0]
            angle = abs(theta1 - theta2) * 180 / np.pi
            if 88 <= angle <= 92:
                print(line1, line2)
                candidate_regions.append((line1, line2))

for line1, line2 in candidate_regions:
    rho1, theta1 = line1[0]
    rho2, theta2 = line2[0]
    
    # 计算直线1的两个点
    a1 = np.cos(theta1)
    b1 = np.sin(theta1)
    x01 = a1 * rho1
    y01 = b1 * rho1
    x1 = int(x01 + 1000 * (-b1))
    y1 = int(y01 + 1000 * a1)
    x2 = int(x01 - 1000 * (-b1))
    y2 = int(y01 - 1000 * a1)
    
    # 计算直线2的两个点
    a2 = np.cos(theta2)
    b2 = np.sin(theta2)
    x02 = a2 * rho2
    y02 = b2 * rho2
    x3 = int(x02 + 1000 * (-b2))
    y3 = int(y02 + 1000 * a2)
    x4 = int(x02 - 1000 * (-b2))
    y4 = int(y02 + 1000 * a2)
    
    # 绘制直线
    cv2.line(thresh, (x1, y1), (x2, y2), (0, 255, 0), 1)
    cv2.line(thresh, (x3, y3), (x4, y4), (0, 255, 0), 1)

# 显示图像
cv2.imshow("Candidate Regions", thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()
# print((candidate_regions[1]))
# 步骤S5：二维码定位与识别
decoded_objects = pylibdmtx.decode(thresh)
for obj in decoded_objects:
    print("Decoded DataMatrix Code:", obj.data.decode('utf-8'))

# # 显示处理结果
# cv2.imshow('Original Image', image)
# cv2.imshow('Opened Image', opened_image)
# cv2.imshow('Smoothed Image', smoothed_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
