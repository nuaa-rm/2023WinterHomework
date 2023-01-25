import random
import math

import cv2
import numpy as np

point2pixel = 100       # 两地图点之间的像素距离
pSize = (3, 3)          # 地图尺寸（同时决定最多存在的点的数目
pNumber = 4             # 点数量（最终可能由于无解少于此设置数量）
ek = 10                 # 边数量系数，越小边越多， [4, 15]

eNumber = round(random.random() * pNumber ** 2 / ek) + pNumber
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
    __points = [[-1] * pSize[0] for _ in range(pSize[1])]
    count = 0
    for i in range(pSize[0]):
        for j in range(pSize[1]):
            if _points[i][j]:
                points.append((i, j))
                __points[i][j] = count
                count += 1
    return points, __points


def roundEdges(points):
    _eNumber = eNumber
    edges = []
    index0 = math.floor(random.random() * len(points))
    p0 = points[index0]
    isUsed[index0] = True
    _iterNumber = 0
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
        isUsed[index1] = True
        edges.append((p0, p1))
        p0 = p1
        _eNumber -= 1
        _iterNumber = 0
    return edges


def p2p(point):
    return int(point[0] * point2pixel + point2pixel / 2), int(point[1] * point2pixel + point2pixel / 2)


def drawEdges(img, edges, nodes):
    for edge in edges:
        cv2.line(img, nodes[edge[0]], nodes[edge[1]], (211, 204, 255), 12)


def drawPoints(img, points):
    for point in points:
        cv2.circle(img, point, 15, (102, 55, 243), -1)
        cv2.circle(img, point, 5, (255, 255, 255), -1)


def generateImage(_pSize=(3, 3), _pNumber=9, _ek=5, _point2pixel=100):
    global point2pixel, pSize, pNumber, eNumber, isUsed
    point2pixel = _point2pixel
    pSize = _pSize
    pNumber = _pNumber
    eNumber = round(random.random() * pNumber ** 2 / _ek) + pNumber
    isUsed = [False] * pNumber
    if pNumber > pSize[0] * pSize[1]:
        return 0
    ps = roundPMap()
    es = roundEdges(ps[0])
    pss = []
    ess = []
    remap = [-1] * len(ps[0])
    count = 0
    for i in range(len(isUsed)):
        if isUsed[i]:
            pss.append(p2p(ps[0][i]))
            remap[i] = count
            count += 1
    for edge in es:
        if not samePoint(edge[0], edge[1]):
            ess.append((remap[ps[1][edge[0][0]][edge[0][1]]], remap[ps[1][edge[1][0]][edge[1][1]]]))
    _image = np.ones((pSize[0] * point2pixel, pSize[1] * point2pixel, 3), np.uint8) * 255
    drawEdges(_image, ess, pss)
    drawPoints(_image, pss)
    return _image, {'nodes': pss, 'edges': ess}
