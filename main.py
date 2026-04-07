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

def check_wake_word():
    import os
    while True:
        if os.path.exists("wake_signal.txt"):
            try:
                os.remove("wake_signal.txt")
                playAssistantSound()
                eel.ShowSiriWave()
                import engine.command
                engine.command.allCommands(1)
            except Exception as e:
                print(e)
        eel.sleep(0.5)

def start():
    eel.init("www")
    
    playAssistantSound()

    os.system('start msedge.exe --app="http://localhost:8000/index.html"')

    # Start the IPC file listener as a gevent greenlet
    eel.spawn(check_wake_word)

    eel.start('index.html', mode=None, host='localhost', block=True, close_callback=close_callback)