#!/usr/bin/sh
rm -rf dist
mkdir dist
cp main.py dist/
cp updater.py dist/
cp config.py dist/
cp -r static dist/
cp -r app dist/
cd dist
easycython updater.py
for i in ./*.so; do
    mv "$i" "${i%%cpython*}so"
done
rm -rf build __pycache__
rm -f ./*.c ./*.html updater.py
cd app
easycython app.py generator.py judge.py
for i in ./*.so; do
    mv "$i" "${i%%cpython*}so"
done
rm -rf build __pycache__
rm -f ./*.c ./*.html app.py generator.py judge.py
rm -f static/images/*
