#!/usr/bin/python3
import updater


if __name__ == '__main__':
    updater.run()
    from app import app
    app.run()
