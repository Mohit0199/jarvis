import gevent.monkey
gevent.monkey.patch_all()

import os
import eel
from engine.features import *
from engine.command import *


def close_callback(route, websockets):
    if not websockets:
        print('Window closed, exiting program...')
        os._exit(0)

def start():
    eel.init("www")

    playAssistantSound()

    os.system('start msedge.exe --app="http://localhost:8000/index.html"')

    eel.start('index.html', mode=None, host='localhost', block=True, close_callback=close_callback)