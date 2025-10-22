import os
import threading
import json
import logging
import atexit
from datetime import datetime
from typing import Dict, Any, Callable
from .apiCore import WebsocketManager

__all__ = [
    'start_api',
    'restart_api',
    'Line',
    'Bar',
    'Sequence',
    'Lines',
    'Bars',
    'Sequences',
    'Scatter',
    'Area',
    'Areas',
    'Pie',
    'Radar',
    'Surface',
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

_manager: WebsocketManager | None = None

def start_config_load():
    from .configEdit import configLoad
    config = configLoad()

    host = config['WEBSOCKET_CONFIG']['HOST']
    port = config['WEBSOCKET_CONFIG']['PORT']
    route = config['WEBSOCKET_CONFIG']['ROUTE']

    return host, port, route

def start_config_check(host: str | None, port: str | None, route: str | None):
    if host is None or port is None or route is None:
        hostDefault, portDefault, routeDefault = start_config_load()
        host = hostDefault if host is None else host
        port = portDefault if port is None else port
        route = routeDefault if route is None else route
    
    return host, port, route

def start_manager(host: str, port: str, route: str):

    global _manager
    
    logging.info("Initializing user API.")
    _manager = WebsocketManager(host=host, port=port, route=route)
    _manager.start_server_thread()
    atexit.register(_manager.stop_server_thread)
    logging.info("User API initialized.")

    return _manager

def start_api(host: str | None=None, port: str | None=None, route: str | None=None):

    global _manager
    
    if _manager is not None:
        logging.info("Data service is already running.")
        return _manager
    else:
        host, port, route = start_config_check(host, port, route)
        return start_manager(host, port, route)

def restart_api(host: str | None=None, port: str | None=None, route: str | None=None):

    global _manager

    if _manager is not None:
        logging.info("Data service is already running, restarting...")
        _manager = None
    else:
        logging.info("Data service is not running, starting...")
    return start_api(host=host, port=port, route=route)


class DataStream:
    """
    Abstract class for data streams, defines the synchronous interface
    that users can call.
    """
    @staticmethod
    def _data_validated(data_payload: Any):
        if (not isinstance(data_payload, dict)) or ("id" not in data_payload) or ("timestamp" not in data_payload) or ("value" not in data_payload):
            return False
        else:
            return True

    @staticmethod
    def _data_validated_number(data_payload: Any):
        from numbers import Number
        if DataStream._data_validated(data_payload) and isinstance(data_payload['value'], Number):
            return True
        else:
            return False

    @staticmethod
    def _data_validated_dict(data_payload: Any):
        if DataStream._data_validated(data_payload) and isinstance(data_payload['value'], dict):
            return True
        else:
            return False

    @staticmethod
    def _data_validated_list(data_payload: Any):
        if DataStream._data_validated(data_payload) and isinstance(data_payload['value'], list):
            return True
        else:
            return False

    @staticmethod
    def _data_validated_coordinate(data_payload: Any):
        from numbers import Number
        if DataStream._data_validated_list(data_payload):
            value = data_payload['value']
            if len(value) == 2:
                x, y = value
                if isinstance(x, Number) and isinstance(y, Number):
                    return True
                else:
                    return False
            else:
                return False 
        else:
            return False

    @staticmethod
    def _data_validated_dimension(data_payload: Any):
        if DataStream._data_validated_list(data_payload):
            value = data_payload['value']
            if len(value) == 2:
                dimension, num = value
                if isinstance(dimension, list) and isinstance(num, list) and len(dimension) == len(num):
                    return True
                else:
                    return False
            return False
        else:
            return False

    @staticmethod
    def _data_validated_dimensions(data_payload: Any):
        if DataStream._data_validated_list(data_payload):
            value = data_payload['value']
            if len(value) == 3:
                dimension, series, num = value
                if isinstance(dimension, list) and isinstance(series, list)  and isinstance(num, list) and len(series) == len(num):
                    return True
                else:
                    return False
            return False
        else:
            return False

    @staticmethod
    def _data_validated_surface(data_payload: Any):
        if DataStream._data_validated_list(data_payload):
            value = data_payload['value']
            if len(value) == 3:
                axis, shape, num = value
                if len(axis) == 3 and len(shape) == 2 and len(num) == shape[0] * shape[1]:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False


    def __init__(self, key_word: str, chart_type: str):
        self.key_word = key_word.strip().lower()
        self.chart_type = chart_type
        self.data_key = self._get_data_key()
        
        # Register itself with the backend Manager so it can be identified when the frontend subscribes
        _manager.register_data_stream(self.data_key)
        logging.info(f"Registered new DataStream: {self.chart_type} -> {self.key_word}")

    def _get_data_key(self) -> str:
        """Generates a unique key for the backend Manager to identify the data stream"""
        return f"{self.chart_type}<:>{self.key_word}"

    def update(self, data_payload: Dict[str, Any]):
        """Updates the data and triggers a push"""
        # Bridge the synchronous call to the asynchronous Manager, which handles cache updates and WebSocket pushes in the background event loop
        _manager.push_update_sync(self.data_key, data_payload)
        logging.debug(f"Pushed update for {self.chart_type} -> {self.key_word}")

    def get_cached_data(self) -> Dict[str, Any] | None:
        return _manager.get_cached_data_sync(self.data_key)
    
    def execute(self, logic_func: Callable, *args, **kwargs):
        """Excute a func at background"""
        
        def thread_target(stream_instance, func, *func_args, **func_kwargs):
            try:
                func(stream_instance, *func_args, **func_kwargs)
            except Exception as e:
                print(f"Error in background thread: {e}")
            finally:
                print(f"Thread finished.")

        thread = threading.Thread(
            target=thread_target, 
            args=(self, logic_func) + args, 
            kwargs=kwargs,
            daemon=True
        )
        
        thread.start()
        logging.info(f"{self.chart_type}('{self.data_key}') calls {logic_func.__name__} in background (daemon) thread.")

    def fresh(self, data_payload_value: Any):
        data_payload = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "timestamp": datetime.now().isoformat(),
            "value": data_payload_value
        }
        self.update(data_payload)


class Line(DataStream):
    def __init__(self, key_word: str):
        super().__init__(key_word, chart_type='line')

    def update(self, data_payload: Dict[str, Any]):
        if not DataStream._data_validated_number(data_payload):
            logging.error(f"Invalid data update form for "+str(self.chart_type)+' -> '+str(self.key_word)+r". Must be like: {id:xxx, timestamp:xxx, value:some_number}")
        else:
            super().update(data_payload)


class Bar(DataStream):
    def __init__(self, key_word: str):
        super().__init__(key_word, chart_type='bar')

    def update(self, data_payload: Dict[str, Any]):
        if not DataStream._data_validated_number(data_payload):
            logging.error(f"Invalid data update form for "+str(self.chart_type)+' -> '+str(self.key_word)+r". Must be like: {id:xxx, timestamp:xxx, value:some_number}")
        else:
            super().update(data_payload)

class Sequence(DataStream):
    def __init__(self, key_word: str):
        super().__init__(key_word, chart_type='sequence')
    
    def update(self, data_payload: Dict[str, Any]):
        if not DataStream._data_validated_number(data_payload):
            logging.error(f"Invalid data update form for "+str(self.chart_type)+' -> '+str(self.key_word)+r". Must be like: {id:xxx, timestamp:xxx, value:some_number}")
        else:
            super().update(data_payload)

class Lines(DataStream):
    def __init__(self, key_word: str):
        super().__init__(key_word, chart_type='lines')

    def update(self, data_payload: Dict[str, Any]):
        if not DataStream._data_validated_dict(data_payload):
            logging.error("Invalid data update form for "+str(self.chart_type)+' -> '+str(self.key_word)+r". Must be like: {id:xxx, timestamp:xxx, value:{A:some_number, B:some_number}}.")
        else:
            super().update(data_payload)

class Bars(DataStream):
    def __init__(self, key_word: str):
        super().__init__(key_word, chart_type='bars')
    
    def update(self, data_payload: Dict[str, Any]):
        if not DataStream._data_validated_dict(data_payload):
            logging.error("Invalid data update form for "+str(self.chart_type)+' -> '+str(self.key_word)+r". Must be like: {id:xxx, timestamp:xxx, value:{A:some_number, B:some_number}}.")
        else:
            super().update(data_payload)

class Sequences(DataStream):
    def __init__(self, key_word: str):
        super().__init__(key_word, chart_type='sequences')
    
    def update(self, data_payload: Dict[str, Any]):
        if not DataStream._data_validated_dict(data_payload):
            logging.error("Invalid data update form for "+str(self.chart_type)+' -> '+str(self.key_word)+r". Must be like: {id:xxx, timestamp:xxx, value:{A:some_number, B:some_number}}.")
        else:
            super().update(data_payload)

class Scatter(DataStream):
    def __init__(self, key_word: str):
        super().__init__(key_word, chart_type='scatter')

    def update(self, data_payload: Dict[str, Any]):
        if not DataStream._data_validated_coordinate(data_payload):
            logging.error("Invalid data update form for "+str(self.chart_type)+' -> '+str(self.key_word)+r". Must be like: {id:xxx, timestamp:xxx, value:[some_number, some_number]}.")
        else:
            super().update(data_payload)

class Area(DataStream):
    def __init__(self, key_word: str):
        super().__init__(key_word, chart_type='area')

    def update(self, data_payload: Dict[str, Any]):
        """
        Data form should be like: {id:xxx, timestamp:xxx, value:[[A, B, C], [1, 2, 3]]}
        First element of value will be used as x-axis tickers,
        Second element of value will be a list of numbers, which are the true value at different x-axis tickers.
        """
        if not DataStream._data_validated_dimension(data_payload):
            logging.error("Invalid data update form for "+str(self.chart_type)+' -> '+str(self.key_word)+r". Must be like: {id:xxx, timestamp:xxx, value:[[A, B, C], [1, 2, 3]]}.")
        else:
            super().update(data_payload)

class Areas(DataStream):
    def __init__(self, key_word: str):
        super().__init__(key_word, chart_type='areas')

    def update(self, data_payload: Dict[str, Any]):
        """
        Data form should be like: {id:xxx, timestamp:xxx, value:[[A, B, C], [label_1, label_2], [[1, 2, 3],[4, 5, 6]]]}
        First element of value will be used as x-axis tickers,
        Second element of value will be label of different data series, 
        Third element of value will be a 2-dimension array, which is the true value of different data series.
        """
        if not DataStream._data_validated_dimensions(data_payload):
            logging.error("Invalid data update form for "+str(self.chart_type)+' -> '+str(self.key_word)+r". Must be like: {id:xxx, timestamp:xxx, value:[[A, B, C], [label_1, label_2], [[1, 2, 3],[4, 5, 6]]]}.")
        else:
            super().update(data_payload)

class Pie(DataStream):
    def __init__(self, key_word: str):
        super().__init__(key_word, chart_type='pie')
    
    def update(self, data_payload: Dict[str, Any]):
        """
        Data form should be like: {id:xxx, timestamp:xxx, value:[[A, B, C], [1, 2, 3]]}
        First element of value will be used as x-axis tickers,
        Second element of value will be a list of numbers, which is the true value at different x-axis tickers.
        """
        if not DataStream._data_validated_dimension(data_payload):
            logging.error("Invalid data update form for "+str(self.chart_type)+' -> '+str(self.key_word)+r". Must be like: {id:xxx, timestamp:xxx, value:[[A, B, C], [1, 2, 3]]}.")
        else:
            super().update(data_payload)

class Radar(DataStream):
    def __init__(self, key_word: str):
        super().__init__(key_word, chart_type='radar')

    def update(self, data_payload: Dict[str, Any]):
        """
        Data form should be like: {id:xxx, timestamp:xxx, value:[[A, B, C], [100, 100, 100], [4, 5, 6]]}
        First element of value will be used as x-axis tickers,
        Second element of value will be max value at different x-axis tickers, 
        Third element of value will be a list of number, which is the true value at different x-axis tickers.
        """
        if not DataStream._data_validated_dimensions(data_payload):
            logging.error("Invalid data update form for "+str(self.chart_type)+' -> '+str(self.key_word)+r". Must be like: {id:xxx, timestamp:xxx, value:[[A, B, C], [100, 100, 100], [4, 5, 6]]}.")
        else:
            super().update(data_payload)

class Surface(DataStream):
    def __init__(self, key_word: str):
        super().__init__(key_word, chart_type='surface')
    
    def update(self, data_payload: Dict[str, Any]):
        """
        Data form should be like: {id:xxx, timestamp:xxx, value:[[A, B, C], [1, 2], [[1.2, 2.2, 9],[3.2, 4.3, 8]]]}
        First element of value will be [x-axis name, y-axis name, z-axis name],
        Second element of value will be shape of value array, which is [number of rows, number of columns], 
        Third element of value will be a list of coordinates, which is like [[x1, y1, z1], [x2, y2, z2]...].
        """
        if not DataStream._data_validated_surface(data_payload):
            logging.error("Invalid data update form for "+str(self.chart_type)+' -> '+str(self.key_word)+r". Must be like: {id:xxx, timestamp:xxx, value:[[A, B, C], [1, 2], [[1.2, 2.2, 9],[3.2, 4.3, 8]]]}.")
        else:
            super().update(data_payload)


