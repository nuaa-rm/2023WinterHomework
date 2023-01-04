import cv2

img = cv2.imread("photos/test.png", cv2.IMREAD_UNCHANGED)

# 转换为灰度图像
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 使用高斯滤波器进行平滑
gray = cv2.GaussianBlur(gray, (3, 3), 0)

cv2.imshow("gray", gray)

# 检测图像中的圆
circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 10, param1=100, param2=15, minRadius=15, maxRadius=40)

# 绘制圆形包围框
for i in circles[0, :]:
    # 圆的坐标
    x, y, r = i[0], i[1], i[2]
    # 绘制圆形包围框
    print(x, y, r)
    cv2.circle(img, (int(x), int(y)), int(r), (0, 255, 0), 2)

# 显示图像
cv2.imshow("detected circles", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
