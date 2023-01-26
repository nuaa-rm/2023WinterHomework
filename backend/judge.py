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


def judge(output, answer):
    nss = pointsCompare(answer['nodes'], output['nodes'])
    es_a = [[nss[3][it[i]] for i in range(2)] for it in output['edges']]

    ess = edgesCompare(answer['edges'], es_a)
    continuity = isEdgesContinuity(es_a)

    return result2dict(output['runtime'], answer, nss, ess, output['nodes'], output['edges'], continuity)


def result2dict(runtime, answer, nss, ess, ns_a, es_a, continuity):
    return {
        'time': '%.4fs' % runtime,
        'co': continuity,
        'ok': continuity and len(ess[1]) == 0 and len(ess[2]) == 0 and len(nss[1]) == 0 and len(nss[2]) == 0,
        'nr': '%.2f%%' % (float(len(nss[0])) / float(len(answer['nodes'])) * 100.),
        'np': '%.2f%%' % (float(len(nss[0])) / float(len(ns_a)) * 100.),
        'er': '%.2f%%' % (float(len(ess[0])) / float(len(answer['edges'])) * 100.),
        'ep': '%.2f%%' % (float(len(ess[0])) / float(len(es_a)) * 100.),
    }

