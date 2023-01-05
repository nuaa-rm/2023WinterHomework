import json
import subprocess
import time

import cv2
import matplotlib.pyplot as plt


def getAnswer(path):
    with open(path, 'r') as f:
        return json.load(f)


def pointsCompare(ps1, ps2):
    _in = []
    _left = []
    _right = []
    used = [False] * len(ps2)
    remap = [-1] * len(ps2)
    for i in range(len(ps1)):
        p1 = ps1[i]
        _use = False
        for j in range(len(ps2)):
            p2 = ps2[j]
            if (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 < 25:
                _in.append(p1)
                _use = True
                used[j] = True
                remap[j] = i
                break
        if not _use:
            _left.append(p1)
    for i in range(len(ps2)):
        if not used[i]:
            _right.append(ps2[i])
    return _in, _left, _right, remap


def edgesCompare(es1, es2):
    _in = []
    _left = []
    _right = []
    used = [False] * len(es2)
    for e1 in es1:
        _use = False
        for j in range(len(es2)):
            e2 = es2[j]
            if e1[0] == e2[0] and e1[1] == e2[1] or e1[0] == e2[1] and e1[1] == e2[0]:
                _in.append(e1)
                _use = True
                used[j] = True
                break
        if not _use:
            _left.append(e1)
    for i in range(len(es2)):
        if not used[i]:
            _right.append(es2[i])
    return _in, _left, _right


def isEdgesContinuity(es):
    ok = True
    last = es[0][1]
    for e in es[1:]:
        if e[0] != last:
            ok = False
            break
        last = e[1]
    return ok


def drawPoints(img, pss):
    _in, _left, _right, _ = pss
    for p in _in:
        cv2.circle(img, p, 15, (102, 55, 243), -1)
        cv2.circle(img, p, 5, (255, 255, 255), -1)
    for p in _right:
        cv2.circle(img, p, 15, (102, 55, 243), -1)
    for p in _left:
        cv2.circle(img, p, 12, (255, 255, 255), -1)


def drawEdges(img, ess, ps):
    _, _left, _right = ess
    for e in _right:
        cv2.line(img, ps[e[0]], ps[e[1]], (150, 150, 150), 12)
    for e in _left:
        cv2.line(img, ps[e[0]], ps[e[1]], (255, 204, 211), 12)


def judge(img_path, answer_path, exec_path):
    img = cv2.imread(img_path)
    answer = getAnswer(answer_path)

    proc = subprocess.Popen(exec_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    start = time.time()
    out, _ = proc.communicate(img_path.encode())
    end = time.time()
    out = out.decode().split('\n')

    nodes_len = int(out[0])
    ns_a = []
    for i in range(nodes_len):
        ns_a.append([float(x) for x in out[i + 1].split(' ')])
    edges_len = int(out[nodes_len + 1])
    es_a = []
    for i in range(edges_len):
        es_a.append([int(x) for x in out[i + nodes_len + 2].split(' ')])
    nss = pointsCompare(answer['nodes'], ns_a)
    es_a = [[nss[3][it[i]] for i in range(2)] for it in es_a]

    ess = edgesCompare(answer['edges'], es_a)

    drawEdges(img, ess, answer['nodes'])
    drawPoints(img, nss)

    print('Time: %.4fs' % (end - start))

    print('Nodes Precision: %.2f%%' % (len(nss[0]) / len(answer['nodes']) * 100))
    if len(nss[1]) > 0:
        for p in nss[1]:
            print('\t(%i, %i)' % (p[0], p[1]))

    print('Nodes Recall: %.2f%%' % (len(nss[0]) / len(ns_a) * 100))
    if len(nss[2]) > 0:
        for p in nss[2]:
            print('\t(%i, %i)' % (p[0], p[1]))

    print('Edges Precision: %.2f%%' % (len(ess[0]) / len(answer['edges']) * 100))
    if len(ess[1]) > 0:
        for e in ess[1]:
            print('\t%s -> %s' %
                  tuple([str(list(int((answer['nodes'][e[i]][j] - 50) / 100) for j in range(2))) for i in range(2)]))

    print('Edges Recall: %.2f%%' % (len(ess[0]) / len(es_a) * 100))
    if len(ess[2]) > 0:
        for e in ess[2]:
            print('\t%s -> %s' %
                  tuple([str(list(int((answer['nodes'][e[i]][j] - 50) / 100) for j in range(2))) for i in range(2)]))

    print('Is edges continuity: %s' % isEdgesContinuity(es_a))

    return img, time, nss, ess


if __name__ == '__main__':
    image = judge('/home/bismarck/2023WinterHomework/images/test.png',
                  'answers/result.json', 'identify_bismarck/cmake-build-debug/identify')
    plt.imshow(image[:, :, ::-1])
    plt.show()
