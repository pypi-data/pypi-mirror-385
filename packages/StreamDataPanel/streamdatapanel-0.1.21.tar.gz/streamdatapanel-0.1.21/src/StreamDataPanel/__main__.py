import time
import logging
import argparse
from . import run_app, init_app, init_simulate

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run(dev: bool=None):
    if dev is None:
        parser = argparse.ArgumentParser(description="StreamDataPanel is a library used to show frequently-freshed data.", prog="python -m StreamDataPanel")
        parser.add_argument('-d', '--dev', action='store_true', help='Start with dev mode.')
        args = parser.parse_args()
        dev = args.dev
    if dev:
        init_app(dev=True)
        init_simulate()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Dev mode terminated.")
    else:
        run_app(dev=False)


if __name__ == "__main__":
    run()