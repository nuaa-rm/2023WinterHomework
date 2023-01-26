import traceback

import config

import subprocess
import threading
import time

window = None


def run(img_path):
    proc = subprocess.Popen(config.exec_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    timeoutThread = TimeOutThread(proc)
    timeoutThread.start()
    start = time.time()
    out, _ = proc.communicate(img_path.encode())
    end = time.time()
    timeoutThread.running = False
    ok = True
    ns_a = []
    es_a = []

    try:
        out = out.decode().split('\n')
        nodes_len = int(out[0])
        for i in range(nodes_len):
            ns_a.append([float(x) for x in out[i + 1].split(' ')])
        edges_len = int(out[nodes_len + 1])
        for i in range(edges_len):
            es_a.append([int(x) for x in out[i + nodes_len + 2].split(' ')])
    except:
        ok = False
        traceback.print_exc()

    return end - start, ns_a, es_a, ok


def errorMsg(msg):
    if window is not None:
        window.evaluate_js(f"window.errorMsg('{msg}')")


class TimeOutThread(threading.Thread):
    running = True

    def __init__(self, proc):
        super().__init__()
        self.proc = proc

    def run(self):
        time.sleep(5)
        if self.running:
            self.proc.terminate()
            errorMsg('程序运行超时！')
            print('Proc run timeout')
