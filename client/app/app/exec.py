import config

import subprocess
import threading
import time
import traceback

window = None
running = False


def exec(img_path):
    global running
    running = True
    proc = subprocess.Popen(config.exec_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    timeoutThread = threading.Thread(target=timeoutHandle, args=(proc,)).start()
    start = time.time()
    out, _ = proc.communicate(img_path.encode(), 4)
    end = time.time()
    running = False
    out = out.decode().split('\n')

    nodes_len = int(out[0])
    ns_a = []
    for i in range(nodes_len):
        ns_a.append([float(x) for x in out[i + 1].split(' ')])
    edges_len = int(out[nodes_len + 1])
    es_a = []
    for i in range(edges_len):
        es_a.append([int(x) for x in out[i + nodes_len + 2].split(' ')])

    return end-start, ns_a, es_a


def errorMsg(msg):
    if window is not None:
        window.evaluate_js(f"window.errorMsg('{msg}')")


def timeoutHandle(proc):
    time.sleep(5)
    if running:
        proc.terminate()
        errorMsg('程序运行超时！')
        print('Proc run timeout')
