from . import procExec

import os

import cv2
import numpy as np

imagesPath = os.path.join(os.path.dirname(__file__), 'static/images')


def drawEdges(img, edges):
    for edge in edges:
        cv2.line(img, edge[0], edge[1], (211, 204, 255), 12)


def drawPoints(img, points):
    for point in points:
        cv2.circle(img, point, 15, (102, 55, 243), -1)
        cv2.circle(img, point, 5, (255, 255, 255), -1)


def drawArrow(img, edge):
    cv2.arrowedLine(img, edge[0], edge[1], (0xff, 0x88, 0x33), 4)


def compute(img_path):
    img = cv2.imread(img_path)
    img_path = os.path.join(imagesPath, 'input.png')
    cv2.imwrite(img_path, img)

    _, ns_a, es_a = procExec.run(img_path)
    es = [[[round(it) for it in ns_a[i]] for i in _e] for _e in es_a]

    for i in range(len(es_a)):
        canvas = np.ones(img.shape) * 255
        drawEdges(canvas, es[:i+1])
        drawPoints(canvas, ns_a)
        drawArrow(canvas, es[i])
        cv2.imwrite(os.path.join(imagesPath, 'output%i.png' % i), canvas)

    return len(es_a) - 1
