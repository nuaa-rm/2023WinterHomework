import traceback

from . import generator, judge, draw, procExec, online

import os
import shutil


import cv2
import webview

launchPath = os.path.join(os.path.dirname(__file__), 'static/index.html')
imagesPath = os.path.join(os.path.dirname(__file__), 'static/images')


def closeWindowCreator(window):
    def closeWindow():
        print("close window")
        window.destroy()
        shutil.rmtree(imagesPath)
        os.mkdir(imagesPath)
        exit(0)
    return closeWindow


def minimizeWindowCreator(window):
    def minimizeWindow():
        print("minimize window")
        window.minimize()
    return minimizeWindow


def localCompute2(req):
    size = req['size']
    en = req['en']
    pn = req['pn']
    if req['mode'] == 'stupid':
        size = 3
        en = 10
        pn = 5
    elif req['mode'] == 'easy':
        size = 4
        en = 10
        pn = 8
    elif req['mode'] == 'normal':
        size = 5
        en = 10
        pn = 15
    img, answer = generator.generateImage((size, size), pn, en)
    cv2.imwrite(os.path.join(imagesPath, 'question.png'), img)
    result = judge.judge(os.path.join(imagesPath, 'question.png'), answer)
    cv2.imwrite(os.path.join(imagesPath, 'result.png'), result[0])
    judge.printResult(*result[1:])
    result = judge.result2dict(*result[1:])
    # if req['export']:
    #     result['mode'] = req['mode']
    #     online.client.submitJudge(result)
    print(result)
    return result


def stepComputeCreator(window):
    def stepCompute():
        shutil.rmtree(imagesPath)
        os.mkdir(imagesPath)
        file_types = ('Image Files (*.bmp;*.jpg;*.gif;*.png)',)
        path = window.create_file_dialog(webview.OPEN_DIALOG, file_types=file_types)
        try:
            return draw.compute(path[0])
        except:
            return 0
    return stepCompute


def login():
    return online.login()


def initClientCreator(window):
    def clearLogin():
        window.evaluate_js("window.clearLogin()")

    def initClient():
        online.client.init()
        online.client.setClearLogin(clearLogin)
        try:
            td = online.getTimeDelta()
        except:
            td = online.getTimeDelta()
        print('cline init!')
        return {'td': td, 'name': online.client.getName()}
    return initClient


def run():
    window = webview.create_window('CKYF 2023WH', launchPath, height=820, width=1280,
                                   resizable=True, frameless=True, transparent=True, easy_drag=False)
    procExec.window = window
    window.expose(
        closeWindowCreator(window),
        minimizeWindowCreator(window),
        localCompute2,
        stepComputeCreator(window),
        login,
        initClientCreator(window),
        *online.client.getFuncs()
    )
    webview.start(gui='gtk', http_server=True, debug=True)
