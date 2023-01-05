import cv2
import numpy as np

a = 50
b = 50
c = 50
d = 150
r = 16


def paint_line_if_color(image, point1, point2, color):
    # 获取直线的长度
    length = int(np.linalg.norm(np.array(point1) - np.array(point2)))

    # 遍历直线上的每个像素
    for i in range(16, length - 16):
        x = int(point1[0] + i * (point2[0] - point1[0]) / length)
        y = int(point1[1] + i * (point2[1] - point1[1]) / length)
        # 获取像素的颜色
        pixel_color = image[y, x]
        # 如果像素的颜色与特定的RGB颜色不同，则不涂色
        if not (pixel_color == color).all():
            return 0

    # 如果所有像素的颜色都与特定的RGB颜色相同，则绘制蓝色的直线
    # cv2.line(image, point1, point2, (255, 0, 0), 2)
    p = (point1, point2)
    # print("Line up:", p)
    return p


# 读入图片
img = cv2.imread("photos/test.png", cv2.IMREAD_UNCHANGED)
paint_line_if_color(img, (a, b), (c, d), [211, 204, 255])
