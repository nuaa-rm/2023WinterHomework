from . import procExec

import cv2


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
    if len(es) <= 1:
        return False
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
        cv2.circle(img, p, 15, (102, 55, 243), -1)
        cv2.circle(img, p, 12, (255, 255, 255), -1)


def drawEdges(img, ess, ps):
    _, _left, _right = ess
    for e in _right:
        cv2.line(img, ps[e[0]], ps[e[1]], (150, 150, 150), 12)
    for e in _left:
        cv2.line(img, ps[e[0]], ps[e[1]], (255, 204, 211), 12)


def judge(img_path, answer):
    img = cv2.imread(img_path)

    runtime, ns_a, es_a, _ = procExec.run(img_path)

    nss = pointsCompare(answer['nodes'], ns_a)
    es_a = [[nss[3][it[i]] for i in range(2)] for it in es_a]

    ess = edgesCompare(answer['edges'], es_a)
    continuity = isEdgesContinuity(es_a)

    drawEdges(img, ess, answer['nodes'])
    drawPoints(img, nss)

    return img, runtime, answer, nss, ess, ns_a, es_a, continuity


def result2dict(runtime, answer, nss, ess, ns_a, es_a, continuity):
    data = {
        'time': '%.4fs' % runtime,
        'co': continuity,
        'ok': continuity and len(ess[1]) == 0 and len(ess[2]) == 0 and len(nss[1]) == 0 and len(nss[2]) == 0,
        'nr': '%.2f%%' % (float(len(nss[0])) / float(len(answer['nodes'])) * 100.),
        'er': '%.2f%%' % (float(len(ess[0])) / float(len(answer['edges'])) * 100.),
    }

    if len(ns_a) != 0:
        data['np'] = '%.2f%%' % (float(len(nss[0])) / float(len(ns_a)) * 100.)
    else:
        data['np'] = 'NaN%'

    if len(es_a) != 0:
        data['ep'] = '%.2f%%' % (float(len(ess[0])) / float(len(es_a)) * 100.)
    else:
        data['ep'] = 'NaN%'

    return data


def printResult(runtime, answer, nss, ess, ns_a, es_a, continuity):
    print('Time: %.4fs' % runtime)

    print('Nodes Recall: %.2f%%' % (len(nss[0]) / len(answer['nodes']) * 100))
    if len(nss[1]) > 0:
        for p in nss[1]:
            print('\t(%i, %i)' % (p[0], p[1]))

    if len(ns_a) != 0:
        print('Nodes Precision: %.2f%%' % (len(nss[0]) / len(ns_a) * 100))
        if len(nss[2]) > 0:
            for p in nss[2]:
                print('\t(%i, %i)' % (p[0], p[1]))
    else:
        print('Nodes Precision: NaN%')

    print('Edges Recall: %.2f%%' % (len(ess[0]) / len(answer['edges']) * 100))
    if len(ess[1]) > 0:
        for e in ess[1]:
            print('\t%s -> %s' %
                  tuple([str(list(int((answer['nodes'][e[i]][j] - 50) / 100) for j in range(2))) for i in range(2)]))

    if len(es_a) != 0:
        print('Edges Precision: %.2f%%' % (len(ess[0]) / len(es_a) * 100))
        if len(ess[2]) > 0:
            for e in ess[2]:
                print('\t%s -> %s' %
                      tuple(
                          [str(list(int((answer['nodes'][e[i]][j] - 50) / 100) for j in range(2))) for i in range(2)]))
    else:
        print('Edges Precision: NaN%')

    print('Is edges continuity: %s' % continuity)
