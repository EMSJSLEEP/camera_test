import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
import zxing  # 导入解析包

class BlobDetector(object):
    def __init__(self, thresholdStep=100, minArea=200, maxArea=5000):
        self.params = cv2.SimpleBlobDetector_Params()
        self.params.thresholdStep = thresholdStep  # 亮度阈值的步长控制，越小检测出来的斑点越多
        self.params.filterByArea = True  # 像素面积大小控制
        self.params.minArea = minArea
        self.params.maxArea = maxArea
        self.detector = cv2.SimpleBlobDetector_create(self.params)  # 创建斑点检测器

    def detect(self, img):
        keypoints = self.detector.detect(img)  # 在哪个图上检测斑点
        print("共检测出%d个斑点" % len(keypoints))
        im_with_keypoints = cv2.drawKeypoints(img, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        blobs = []
        for kp in keypoints:
            blobs.append((int(kp.pt[0]), int(kp.pt[1])))

        plt.subplot(1, 1, 1)
        plt.imshow(cv2.cvtColor(im_with_keypoints, cv2.COLOR_BGR2RGB))
        plt.title("OpenCV 斑点检测", fontsize=16, color="b")
        plt.show()
        return blobs
    
def detect_blobs_using_contours(img):
    # 寻找图像中的轮廓
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 初始化空白矩阵
    blobs = np.zeros(img.shape, dtype=np.uint8)
    
    # 绘制轮廓
    for cnt in contours:
        cv2.drawContours(blobs, [cnt], 0, (255), -1)  # 将轮廓填充为白色

    return blobs, contours

def ocr_qrcode_zxing(filename):
    zx = zxing.BarCodeReader()  # 调用zxing二维码读取包
    zxdata = zx.decode(filename)  # 图片解码
    return zxdata.parsed  # 返回记录的内容

# 图像预处理
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

blobs, contours = detect_blobs_using_contours(thresh)
plt.imshow(blobs, cmap='gray')
plt.title('Detected Blobs Using Contours')
plt.show()
# 斑点识别
blobDetector = BlobDetector()
blobs = blobDetector.detect(thresh)

# 根据各斑点之间的相对位置，将斑点阵列转换为值为0（0代表斑点）和1的矩阵
blobs.sort(key=lambda L: L[1])  # 按行排序
blob_X = [x for (x, y) in blobs]
blob_Y = [y for (x, y) in blobs]

# 18行*18列的二维码
index_ychange = []
last_y = blob_Y[0]
for i, y in enumerate(blob_Y):
    if y - last_y > 3:  # 像素间隔
        index_ychange.append(i)
    last_y = y

index_xchange = []
blob_X.sort()
last_x = blob_X[0]
for i, x in enumerate(blob_X):
    if x - last_x > 3:  # 像素间隔
        index_xchange.append(i)
    last_x = x

A = np.ones((18, 18), dtype=np.uint8)
j = 0
start = 0
index_ychange.append(len(blobs))
index_xchange.append(len(blobs))

for _ in index_ychange:
    for k in range(start, _):
        x = blobs[k][0]  # 像素坐标
        x_index = blob_X.index(x)
        for i, m in enumerate(index_xchange):
            if x_index < m:
                break
        A[j, i] = 0  # 有斑点的位置为0
    start = _
    j += 1

for row in A:
    print(row)

A *= 255  # 变成黑白图像数组

# 周围填充白色方便识别
N = 20
B = np.ones((N, N), dtype=np.uint8) * 255
B[(N-18)//2:N-(N-18)//2, (N-18)//2:N-(N-18)//2] = A

plt.subplot(1, 1, 1)
plt.imshow(B, cmap="gray")
plt.title("OpenCV 斑点检测", fontsize=16, color="b")
plt.show()

# 放大图像，提高识别率
rows, cols = B.shape
k = 2
C = np.zeros((rows*k, cols*k), dtype=np.uint8)
for i in range(rows):
    for j in range(cols):
        C[k*i:k*(i+1), k*j:k*(j+1)] = B[i, j]

cv2.imwrite('test.bmp', C)

result = ocr_qrcode_zxing("test.bmp")
print(result)
