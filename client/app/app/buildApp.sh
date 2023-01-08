#!/usr/bin/bash
SCRIPT_PATH="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"
cd "$SCRIPT_PATH" || exit
echo "$SCRIPT_PATH"
easycython app.py generator.py judge.py draw.py exec.py
for i in ./*.so; do
    mv "$i" "${i%%cpython*}so"
done
rm -rf build
rm -f ./*.c ./*.html app.py generator.py judge.py draw.py exec.py
