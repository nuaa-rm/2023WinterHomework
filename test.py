import generator
import judge

import os

import matplotlib.pyplot as plt
import cv2

if __name__ == '__main__':
    img_path = os.path.join(os.path.dirname(__file__), 'images/test.png')
    image = generator.generateImage(100, (6, 6), 36, 5)
    cv2.imwrite(img_path, image)
    res = judge.judge(img_path, 'answers/result.json', 'identify_bismarck/cmake-build-debug/identify')
    judge.printResult(*res[1:])
    plt.imshow(res[0][:, :, ::-1])
    plt.show()
