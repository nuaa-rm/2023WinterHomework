import random
import math

import cv2
import numpy as np

point2pixel = 200
pSize = (3, 3)
pNumber = 5
eNumber = round(random.random() * pNumber / 2) + pNumber


def roundPoint():
    return math.floor(random.random() * pSize[1]), math.floor(random.random() * pSize[1])


def samePoint(p1, p2):
    return p1[0] == p2[0] and p1[1] == p2[1]


def sameEdge(e1, e2):
    return samePoint(e1[0], e2[0]) and samePoint(e1[1], e2[1]) or samePoint(e1[0], e2[1]) and samePoint(e1[1], e2[0])


def lineValid(edge):
    e = [abs(edge[0][i] - edge[1][i]) for i in range(2)]
    ok = True
    for i in range(2, max(pSize)+1):
        _e = [e[j] / i for j in range(2)]
        _e = [abs(_e[j] - round(_e[j])) for j in range(2)]
        if _e[0] < 1e-2 and _e[1] < 1e-2:
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
    p0 = points[math.floor(random.random() * len(points))]
    print(p0)
    while _eNumber > 0:
        p1 = points[math.floor(random.random() * len(points))]
        if samePoint(p0, p1):
            continue
        if not lineValid((p0, p1)):
            continue
        has = False
        for edge in edges:
            if sameEdge(edge, (p0, p1)):
                has = True
                break
        if has:
            continue
        print(p1)
        edges.append((p0, p1))
        p0 = p1
        _eNumber -= 1
    return edges


def p2p(point):
    return int(point[0] * point2pixel + point2pixel / 2), int(point[1] * point2pixel + point2pixel / 2)


def drawEdges(img, edges):
    for edge in edges:
        cv2.line(img, p2p(edge[0]), p2p(edge[1]), (211, 204, 255), 12)


def drawPoints(img, points):
    for point in points:
        cv2.circle(img, p2p(point), 15, (102, 55, 243), -1)
        cv2.circle(img, p2p(point), 5, (255, 255, 255), -1)


if __name__ == '__main__':
    ps = roundPMap()
    es = roundEdges(ps[0])
    image = np.ones((pSize[0] * point2pixel, pSize[1] * point2pixel, 3), np.uint8) * 255
    drawEdges(image, es)
    drawPoints(image, ps[0])
    cv2.imshow("test", image)
    cv2.waitKey(0)
