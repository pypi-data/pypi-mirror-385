#!/usr/bin/python
#coding = utf-8
import eel
import os
import argparse
import logging

from .configEdit import config_load, config_reset, config_update
from .api import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CONFIG = config_load()

APP_CONFIG = CONFIG['APP_CONFIG']

EEL_CONFIG = CONFIG['EEL_CONFIG']

def thread_target(func, *func_args, **func_kwargs):
    try:
        func(*func_args, **func_kwargs)
    except BaseException as e: 
        if isinstance(e, (SystemExit, KeyboardInterrupt)):
            logging.info(f"Thread received shutdown signal ({e.__class__.__name__}).")
        else:
            logging.error(f"Error in background thread: {e}", exc_info=True)
    finally:
        logging.info(f"Thread finished.")

@eel.expose
def get_initial_config():
    logging.info("Initializing...")
    return APP_CONFIG

def run_app(dev: bool=None):
    if dev is None:
        parser = argparse.ArgumentParser()
        parser.add_argument('-d', '--dev', action='store_true', help='start with dev mode')
        args = parser.parse_args()
        dev = args.dev
    if dev:
        port = EEL_CONFIG['PORT_DEV']
        logging.info(f"Running in Development Mode, Port: {port}")
        eel.init('')
        eel.start('', mode=None, port=port, host='localhost')
    else:
        port = EEL_CONFIG['PORT']
        size = tuple(EEL_CONFIG['SIZE'])
        eel.init(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web'))
        eel.start('index.html', size=size, mode='default', port=port)

def init_app(dev: bool=None):
    if dev is None:
        parser = argparse.ArgumentParser()
        parser.add_argument('-d', '--dev', action='store_true', help='start with dev mode')
        args = parser.parse_args()
        dev = args.dev
    from threading import Thread
    app = Thread(target=thread_target, args=(run_app,), kwargs={'dev': dev}, daemon=True)
    app.start()

def init_simulate():
    from .apiTest import simulate_all
    start_api()
    simulate_all()

def test():
    from time import sleep
    from threading import Thread
    
    init_app()
    init_simulate()

    try:
        logging.info('Running test...')
        sleep(300)
    except KeyboardInterrupt:
        logging.info("Test terminated.")

def set_config(config_type: str=None, config_item: str=None, config_value: str | int=None):
    if config_type is None and config_item is None and config_value is None:
        parser = argparse.ArgumentParser()
        parser.add_argument('config_type', help='it should be APP_CONFIG or VITE_CONFIG or EEL_CONFIG or WEBSOCKET_CONFIG, etc')
        parser.add_argument('config_item', help='it should be PORT or TITLE, etc. print config to see which can be used')
        parser.add_argument('config_value', help='it should be a string or a number')
        args = parser.parse_args()
        config_type = args.config_type
        config_item = args.config_item
        config_value = args.config_value
    config_update(config_type, config_item, config_value)

def show_config():
    content = config_load()
    print(content)

def reset_config():
    config_reset()


