import os
import traceback

exec_path = '/home/bismarck/2023WinterHomework/identify_bismarck/cmake-build-debug/identify'
versionFilePath = os.path.join(os.path.dirname(__file__), 'app/version.txt')


def getLocalVersion():
    try:
        with open(versionFilePath, 'r') as f:
            return float(f.read())
    except Exception:
        traceback.print_exc()
        return -1
