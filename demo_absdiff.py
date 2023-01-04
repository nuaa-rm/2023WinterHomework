import cv2
import numpy as np

image = cv2.imread("photos/test.png", cv2.IMREAD_GRAYSCALE)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
dilate_img = cv2.dilate(image, kernel)
erode_img = cv2.erode(image, kernel)

absdiff_img = cv2.absdiff(dilate_img, erode_img)
retval, threshold_img = cv2.threshold(absdiff_img, 40, 255, cv2.THRESH_BINARY)
result = cv2.bitwise_not(threshold_img)

cv2.imshow("raw", image)
cv2.imshow("dilate_img", dilate_img)
cv2.imwrite("photos/dilate_img.png", dilate_img)
cv2.imshow("erode_img", erode_img)
cv2.imwrite("photos/erode_img.png", erode_img)
cv2.imshow("absdiff_img", absdiff_img)
cv2.imwrite("photos/absdiff_img.png", absdiff_img)
cv2.imshow("threshold_img", threshold_img)
cv2.imwrite("photos/threshold_img.png", threshold_img)
cv2.imshow("result", result)
cv2.imwrite("photos/result.png", result)
cv2.waitKey(0)
cv2.destroyAllWindows()
