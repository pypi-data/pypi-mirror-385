import sys,os
import asyncio
import threading
import json
import logging
from typing import Dict, Any, Set, Deque, Callable, Awaitable
from collections import deque
from websockets.server import serve, WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Asynchronous wrapper to handle synchronous data retrieval in user code, returning initial/cached data on frontend subscription
async def _simulate_initial_data_fetch(data_key: str, cache_data: Dict[str, Any], all_valid_keys: Set[str]):
    """Simulates data check and retrieval upon frontend subscription"""
    if data_key not in all_valid_keys:
        logger.error(f'Subscribed key does not exist. Subscribed as {data_key}, Validated keys are {all_valid_keys}')
        return None # Subscribed key does not exist
        
    if data_key in cache_data:
        # If cached, return the cache directly
        return cache_data[data_key]
    else:
        # Simulate generating an empty or default initial data structure
        chart_type, key_word = data_key.split('<:>', 1)
        return {
            "id": "INIT",
            "timestamp": "N/A",
            "value": 0
        }


class WebsocketManager:
    """Backend manager that runs the WebSocket server and asyncio event loop in a separate thread. It acts as a bridge between synchronous and asynchronous code."""
    def __init__(self, host: str, port: int, route: str):
        
        # Connection info
        self.host = host
        self.port = port
        self.route = route

        # Asynchronous core components
        self.loop: asyncio.AbstractEventLoop = None
        self._server_task: asyncio.Task = None
        
        # Thread components
        self._server_thread: threading.Thread = None
        self._is_running = False
        
        # Data and connection management, accessed in the async thread, requires protection 
        self._cache: Dict[str, Dict[str, Any]] = {} 
        self._subscriptions: Dict[str, Set[WebSocketServerProtocol]] = {}
        self._valid_data_keys: Set[str] = set() # Records all valid keys registered by the user via Line('test')
        
        # Sync/Async communication queue, used to bridge synchronous calls to the asynchronous loop
        self._update_queue: Deque[tuple[str, Dict[str, Any]]] = deque()
        self._update_event: asyncio.Event = asyncio.Event() # Notifies the async loop that new data is available

        # Thread Lock
        self._lock = threading.Lock()

    # Synchronous call bridge functions for the user-facing API

    def register_data_stream(self, data_key: str):
        """Called by the user to register a data stream"""
        with self._lock:
            self._valid_data_keys.add(data_key)

    def push_update_sync(self, data_key: str, data_payload: Dict[str, Any]):
        """Called by the user, puts data into the queue"""
        self._update_queue.append((data_key, data_payload))
        if self.loop and self.loop.is_running():
             # Wakes up the background thread to process data
            self.loop.call_soon_threadsafe(self._update_event.set)
    
    def get_cached_data_sync(self, data_key: str) -> Dict[str, Any] | None:
        """Reads the cache"""
        with self._lock:
            return self._cache.get(data_key)
        
    # Thread management

    def start_server_thread(self):
        """Starts the background thread to run the WebSocket server"""
        if self._is_running:
            return
        self._is_running = True
        self._server_thread = threading.Thread(target=self._run_in_thread, daemon=True)
        self._server_thread.start()
        logger.info("WebsocketManager started in background thread.")

    def _run_in_thread(self):
        """Thread entry function, sets up the asyncio event loop and runs the server"""
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Start the WebSocket server and data processing task
            self.loop.create_task(self._start_server_and_loop())
            self.loop.run_forever()
        except KeyboardInterrupt:
            logger.info("Background server thread interrupted.")
        except Exception as e:
            logger.error(f"Background server thread error: {e}")
        finally:
            self.loop.stop()
            self._is_running = False

    def stop_server_thread(self):
        if not self._is_running:
            return

        self._is_running = False
        self._update_event.set()
        
        if self.loop and self.loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self._shutdown_async(), self.loop)
            try:
                future.result(timeout=5)
            except:
                logger.error("Asynchronous shutdown timed out or failed.")
        
        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(timeout=2)
            if self._server_thread.is_alive():
                 logger.warning("Background thread did not terminate gracefully.")

    async def _shutdown_async(self):

        close_tasks = []
        # Collect all alive websocket
        active_websockets = set()
        for subscriptions in self._subscriptions.values():
            active_websockets.update(subscriptions)

        for websocket in active_websockets:
            # Send close order gracefully (code=1000)
            close_tasks.append(websocket.close(code=1000, reason="Server shutting down"))
        
        # Close
        if close_tasks:
            # Make sure all action is finished
            await asyncio.gather(*close_tasks, return_exceptions=True)

        # Cancell server
        if self._server_task:
            self._server_task.cancel()
            
        # Cancel tasks
        tasks = [t for t in asyncio.all_tasks(self.loop) if t is not self._server_task and t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        
        # Stop event loop
        self.loop.call_soon_threadsafe(self.loop.stop)

    async def _start_server_and_loop(self):
            """Starts the WebSocket server and data processing coroutine in the asynchronous loop"""
            
            # Start the WebSocket server
            try:
                # serve() returns an awaitable, convert this awaitable into a task
                server = await serve(
                    self._websocket_handler, 
                    self.host, 
                    self.port, 
                    subprotocols=["json"]
                )
                server_coroutine = server.serve_forever() # Get a coroutine task that runs indefinitely
                self._server_task = self.loop.create_task(server_coroutine)
                logger.info(f"WebSocket Server running on ws://{self.host}:{self.port}")
            except Exception as e:
                logger.error(f"Failed to start WebSocket server: {e}")
                return # Exit if startup fails
            # Start the synchronous data queue processing coroutine
            self.loop.create_task(self._process_update_queue())

    # --- Asynchronous Core Logic ---

    async def _process_update_queue(self):
        """Periodically or event-driven checks the synchronous queue and handles data push"""
        while self._is_running:
            # Use wait_for to wait for event or timeout
            await self._update_event.wait()
            self._update_event.clear()
            
            # Check for new data
            while self._update_queue:
                try:
                    data_key, new_data = self._update_queue.popleft()
                    # Execute update and push in the asynchronous loop
                    await self._update_and_push_async(data_key, new_data)
                except Exception as e:
                    logger.error(f"Error processing update queue: {e}")


    async def _update_and_push_async(self, data_key: str, new_data: Dict[str, Any]):
        """Asynchronously updates the cache and pushes to subscribers"""
        
        # Update cache
        self._cache[data_key] = new_data
        
        # Get the set of subscribers
        subscribers = self._subscriptions.get(data_key, set())
        
        if not subscribers:
            logger.debug(f"Data updated for {data_key}, but no active subscribers.")
            return

        # Asynchronous parallel push
        message = json.dumps(new_data)
        tasks = []
        disconnected_websockets = set()
        
        for websocket in subscribers:
            tasks.append(self._safe_send(websocket, message, disconnected_websockets))
        
        await asyncio.gather(*tasks)

        # Clean up disconnected connections
        if disconnected_websockets:
            self._subscriptions[data_key] -= disconnected_websockets
            logger.info(f"Cleaned up {len(disconnected_websockets)} disconnected clients for {data_key}.")
            if not self._subscriptions[data_key]:
                del self._subscriptions[data_key]
                logger.info(f"No subscribers left for {data_key}. Cleaning up subscription entry.")

    # --- WebSocket Protocol Handling ---

    async def _websocket_handler(self, websocket: WebSocketServerProtocol, path: str):
        """Handles new WebSocket connections and subscriptions"""
        client_address = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        data_key = "" # Used to clean up subscription upon disconnection

        if self.route and path != self.route:
            logger.warning(f"Invalid subscription request from '{client_address}'. Connection attempt on invalid path: {path}. Expected: {self.route}")
            await websocket.send(json.dumps({"status": "failure", "message": "Connection attempt on invalid path."}))
            await websocket.close(code=1008, reason="Connection attempt on invalid path.")
            return

        try:
            # Receive subscription message (expecting the frontend to send {"chart_type": "...", "key_word": "..."})
            subscription_message_raw = await websocket.recv()
            subscription_message = json.loads(subscription_message_raw)
            
            chart_type = subscription_message.get("chart_type")
            key_word = subscription_message.get("key_word")
            data_key = f"{chart_type}<:>{key_word}"

            # Check if the data stream has been registered by the user
            initial_data = await _simulate_initial_data_fetch(data_key, self._cache, self._valid_data_keys)
            
            if initial_data is None:
                logger.warning(f"Invalid subscription request from '{client_address}': chart_type='{chart_type}', key_word='{key_word}'.")
                await websocket.send(json.dumps({"status": "failure", "message": "Invalid chart type or keyword (not registered)."}))
                await websocket.close(code=1008, reason="Invalid subscription format.")
                return

            # Register subscription, add WebSocket to the set
            if data_key not in self._subscriptions:
                self._subscriptions[data_key] = set()
                
            self._subscriptions[data_key].add(websocket)
            logger.info(f"Client '{client_address}' subscribing to: chart_type='{chart_type}', key_word='{key_word}'. Total subscription: {len(self._subscriptions[data_key])}")

            # Successful response, and push initial/cached data
            await websocket.send(json.dumps({"status": "success", "message": "Subscription successful."}))
            # Push cached data
            await websocket.send(json.dumps(initial_data))
            
            # Keep the connection open, waiting for disconnection or message reception, e.g., unsubscribe message
            async for message in websocket:
                # Can handle unsubscribe or other control commands here
                logger.debug(f"Received message from {client_address}: {message}")
                pass
            
        # Catch Exception
        except ConnectionClosedOK:
            logger.info(f"Client disconnected gracefully: {client_address}")
        except asyncio.CancelledError: 
            logger.info(f"Connection task cancelled for: {client_address}")
        except ConnectionClosedError as e:
            # Client broken with exception
            logger.info(f"Client disconnected unexpectedly: {client_address} - {e}")
        except json.JSONDecodeError:
            logger.error(f"Received malformed JSON from client: {client_address}")
        except Exception as e:
            logger.error(f"Error handling connection with {client_address}: {type(e).__name__} - {e}")
        finally:
            # Connection disconnected, remove subscription
            if data_key and websocket in self._subscriptions.get(data_key, set()):
                self._subscriptions[data_key].remove(websocket)
                logger.info(f"Client {client_address} unsubscribed from {data_key}. Remaining: {len(self._subscriptions[data_key])}")


    async def _safe_send(self, websocket: WebSocketServerProtocol, message: str, disconnected_websockets: Set[WebSocketServerProtocol]):
        """Safely sends a message, catching connection closed exceptions"""
        try:
            await websocket.send(message) 
        except Exception as e:
            logger.error(f"Unexpected error during WebSocket send: {e}", exc_info=True)
            disconnected_websockets.add(websocket)