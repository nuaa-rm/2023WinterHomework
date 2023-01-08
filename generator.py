import random
import math

import cv2
import numpy as np

point2pixel = 100  # 两地图点之间的像素距离
pSize = (4, 4)  # 地图尺寸（同时决定最多存在的点的数目
pNumber = 15  # 点数量（最终可能由于无解少于此设置数量）
ek = 5  # 边数量系数，越小边越多， [4, 15]

eNumber = round(random.random() * pNumber ** 2 / 10) + pNumber
isUsed = [False] * pNumber


def rand(num):
    return math.floor(random.random() * num)


def roundPoint():
    return rand(pSize[1]), rand(pSize[1])


def samePoint(p1, p2):
    return p1[0] == p2[0] and p1[1] == p2[1]


def sameEdge(e1, e2):
    return samePoint(e1[0], e2[0]) and samePoint(e1[1], e2[1]) or samePoint(e1[0], e2[1]) and samePoint(e1[1], e2[0])


def lineValid(edge, points):
    e = [edge[1][i] - edge[0][i] for i in range(2)]
    length2 = e[0] ** 2 + e[1] ** 2
    angle = math.atan2(e[1], e[0])
    ok = True
    for point in points:
        _e = [point[i] - edge[0][i] for i in range(2)]
        _angle = math.atan2(_e[1], _e[0])
        if abs(_angle - angle) < 0.01:
            _length = _e[0] ** 2 + _e[1] ** 2
            if _length < length2:
                ok = False
                break
    return ok


def roundPMap():
    _pNumber = pNumber
    _points = [[False] * pSize[0] for _ in range(pSize[1])]
    while _pNumber > 0:
        p = roundPoint()
        if not _points[p[0]][p[1]]:
            _pNumber -= 1
            _points[p[0]][p[1]] = True
    points = []
    for i in range(pSize[0]):
        for j in range(pSize[1]):
            if _points[i][j]:
                points.append((i, j))
    return points, _points


def roundEdges(points):
    _eNumber = eNumber
    edges = []
    index0 = math.floor(random.random() * len(points))
    p0 = points[index0]
    isUsed[index0] = True
    _iterNumber = 0
    print(p0)
    while _eNumber > 0 and _iterNumber < pNumber * 5:
        index1 = math.floor(random.random() * len(points))
        p1 = points[index1]
        if index0 == index1:
            _iterNumber += 1
            continue
        if not lineValid((p0, p1), points):
            _iterNumber += 1
            continue
        has = False
        for edge in edges:
            if sameEdge(edge, (p0, p1)):
                has = True
                break
        if has:
            _iterNumber += 1
            continue
        print(p1)
        isUsed[index1] = True
        edges.append((p0, p1))
        p0 = p1
        _eNumber -= 1
        _iterNumber = 0
    return edges


def p2p(point):
    return int(point[0] * point2pixel + point2pixel / 2), int(point[1] * point2pixel + point2pixel / 2)


def drawEdges(img, edges):
    for edge in edges:
        cv2.line(img, p2p(edge[0]), p2p(edge[1]), (211, 204, 255), 12)


def drawPoints(img, points):
    for i in range(len(points)):
        if isUsed[i]:
            point = points[i]
            cv2.circle(img, p2p(point), 15, (102, 55, 243), -1)
            cv2.circle(img, p2p(point), 5, (255, 255, 255), -1)


if __name__ == '__main__':
    if pNumber > pSize[0] * pSize[1]:
        exit(-1)
    ps = roundPMap()
    es = roundEdges(ps[0])
    image = np.ones((pSize[0] * point2pixel, pSize[1] * point2pixel, 3), np.uint8) * 255
    drawEdges(image, es)
    drawPoints(image, ps[0])
    cv2.imshow("test", image)
    cv2.imwrite("photos/test.png", image)
    cv2.waitKey(0)
