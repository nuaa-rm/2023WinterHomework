import math
import cv2

from paint_line_if_color import paint_line_if_color

img = cv2.imread("photos/test.png", cv2.IMREAD_UNCHANGED)
loc_max = 0
points = []
p = []

image = cv2.imread("photos/test.png", cv2.IMREAD_GRAYSCALE)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
dilate_img = cv2.dilate(image, kernel)
erode_img = cv2.erode(image, kernel)

absdiff_img = cv2.absdiff(dilate_img, erode_img)
retval, threshold_img = cv2.threshold(absdiff_img, 40, 255, cv2.THRESH_BINARY)
result = cv2.bitwise_not(threshold_img)
cv2.imshow("circles", result)
circles = cv2.HoughCircles(result, cv2.HOUGH_GRADIENT, 1, 10, param1=100, param2=15, minRadius=15, maxRadius=30)

# 绘制圆形包围框
for i in circles[0, :]:
    # 圆的坐标
    x, y, r = i[0], i[1], i[2]
    # 绘制圆形包围框
    if x > loc_max:
        loc_max = x
    if y > loc_max:
        loc_max = y
    times = math.ceil(loc_max / 50)
    for tmp in range(times):
        if 50 * tmp - 5 < x < 50 * tmp + 5:
            x = 50 * tmp
        if 50 * tmp - 5 < y < 50 * tmp + 5:
            y = 50 * tmp
    points.append((x, y))
    cv2.circle(img, (x, y), int(r + 2), (211, 204, 255), -1)

# 显示图像
cv2.imshow("pink", img)
cv2.imwrite("photos/detected_circles_hough.png", img)

processed_points = {}

for point_1 in points:
    for point_2 in points:
        if point_1 == point_2 or (point_1, point_2) in processed_points:
            continue
        processed_points[(point_1, point_2)] = True
        if paint_line_if_color(img, point_1, point_2, [211, 204, 255]) != 0:
            print(point_1, point_2)
            p.append(paint_line_if_color(img, point_1, point_2, [211, 204, 255]))

img = cv2.imread("photos/test.png", cv2.IMREAD_UNCHANGED)
for point in p:
    cv2.line(img, point[0], point[1], (0, 255, 0), 2)
cv2.imshow("result", img)
cv2.waitKey(0)
cv2.destroyAllWindows()