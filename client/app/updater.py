import config

import tempfile
import threading
import time
import traceback
import os
import shutil
import zipfile

import webview
import oss2

akid = ''
aksc = ''
auth = oss2.Auth(akid, aksc)
bucket = oss2.Bucket(auth, 'http://oss-cn-hangzhou.aliyuncs.com', 'ckyf-updater')
appPath = os.path.join(os.path.dirname(__file__), 'app')
launchPath = os.path.join(os.path.dirname(__file__), 'static/index.html')


def getCloudVersion():
    with tempfile.TemporaryDirectory() as dirName:
        path = os.path.join(dirName, 'version.txt')
        try:
            bucket.get_object_to_file('version.txt', path)
            with open(path, 'r') as f:
                return float(f.read())
        except Exception:
            traceback.print_exc()
            return -1


def getLocalVersion():
    return config.getLocalVersion()


def msgHook(window: webview.Window, msg):
    window.evaluate_js(f"window.msgHook('{msg}')")


def warnHook(window: webview.Window, msg):
    window.evaluate_js(f"window.statusHook(1, '{msg}')")


def update(version):
    with tempfile.TemporaryDirectory() as dirName:
        path = os.path.join(dirName, '2023WH.zip')
        try:
            bucket.get_object_to_file('2023WH-%.2f.zip' % version, path)
            try:
                if os.path.exists(appPath):
                    shutil.rmtree(appPath)
                os.mkdir(os.path.join(dirName, 'app'))
                with zipfile.ZipFile(path, 'r') as zip:
                    zip.extractall(os.path.join(dirName, 'app'))
                    os.system('chmod +x %s' % os.path.join(dirName, 'app/buildApp.sh'))
                    os.system(os.path.join(dirName, 'app/buildApp.sh'))
                shutil.move(os.path.join(dirName, 'app'), appPath)
                try:
                    from app import app
                except Exception:
                    traceback.print_exc()
                    return 3
                return 0
            except Exception:
                traceback.print_exc()
                return 2
        except Exception:
            traceback.print_exc()
            return 1


def updateProc(window):
    cloudVersion = getCloudVersion()
    if cloudVersion < 0:
        warnHook(window, "更新失败！将在下次启动时重试")
        time.sleep(6)
        window.destroy()
        return
    localVersion = getLocalVersion()
    print(f'Now Cloud Version: {cloudVersion}')
    print(f'Now Local Version: {localVersion}')
    if cloudVersion > localVersion:
        msgHook(window, "正在更新...")
        status = update(cloudVersion)
        if status == 0:
            msgHook(window, "更新成功！即将启动")
        elif status == 1:
            warnHook(window, "更新失败！将在下次启动时重试")
            time.sleep(4)
        elif status == 2:
            warnHook(window, "严重错误！请联系管理员")
            time.sleep(8)
            window.destroy()
            exit(-1)
        elif status == 3:
            warnHook(window, "严重错误！请重新启动程序")
            time.sleep(4)
            window.destroy()
            exit(-1)
    time.sleep(2)
    window.destroy()


def run():
    window = webview.create_window('CKYF Updater', launchPath, height=250, width=500,
                                   resizable=False, frameless=True, transparent=True)
    updateThread = threading.Thread(target=updateProc, args=(window,)).start()
    webview.start(gui='gtk', http_server=True)
    print('Update Done')
