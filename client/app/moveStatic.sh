#!/usr/bin/bash
SCRIPT_PATH="$( cd "$( dirname "$0" )" >/dev/null 2>&1 && pwd )"
echo "$SCRIPT_PATH"
cd "$SCRIPT_PATH" || exit

cd app || exit
rm -rf static/*
mkdir static/images
cp -r ../../web/app/build/* ./static/
