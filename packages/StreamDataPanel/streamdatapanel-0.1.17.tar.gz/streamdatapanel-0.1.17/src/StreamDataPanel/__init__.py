#!/usr/bin/python
#coding = utf-8

import eel
import os
import json

pathFile = os.path.dirname(os.path.abspath(__file__))
pathJson = os.path.join(pathFile, 'config.json' )

with open(pathJson, 'r', encoding='utf-8') as f:
    config = json.load(f)

APP_CONFIG = config['APP_CONFIG']

EEL_CONFIG = config['EEL_CONFIG']

@eel.expose
def get_initial_config():
    print("Initializing...")
    return APP_CONFIG

def run():
    if os.environ.get('EEL_DEVELOPMENT_MODE') == 'true':
        port = EEL_CONFIG['PORT_DEV']
        print(f"Running in Development Mode, Port: {port}")
        eel.init('')
        eel.start('', mode=None, port=port, host='localhost')
    else:
        port = EEL_CONFIG['PORT']
        size = tuple(EEL_CONFIG['SIZE'])
        eel.init(os.path.join(pathFile, 'web'))
        eel.start('index.html', size=size, mode='default', port=port)

def simulate():
    from .apiTest import simulateAll
    simulateAll()

