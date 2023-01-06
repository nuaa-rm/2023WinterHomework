#!/usr/bin/sh
rm -rf dist
mkdir dist
cp main.py dist/
cp updater.py dist/
cp -r static dist/
cp -r app dist/
cd dist
easycython updater.py
rename ".cpython-310-x86_64-linux-gnu.so" ".so" ./*
rm -rf build
rm -f ./*.c ./*.html updater.py
