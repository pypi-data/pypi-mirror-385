from __future__ import annotations
import asyncio
import json
import os
import threading
import time
from typing import Any, Callable, Optional, Awaitable, Dict
from urllib.parse import quote
import logging

try:
    import websockets
    # Explicitly import State for robust connection checking
    from websockets.protocol import State

except Exception as e:
    raise ImportError("Please install the 'websockets' package (pip install websockets) to use NikkiClient") from e

# Defaults adapted from node nikkiDef
SERVICE_DEF_FILE = "serviceDef.json"
SERVICE_TOKEN_FILE = "serviceToken.json"
QUERY_STRING_KEY = "token"
OUT_DATA_SIZE_MAX_LIMIT = 3000
# Node.js segment size limit for input data payload
OUT_DATA_SIZE_SEGMENT_MAX_LIMIT = 500
RECONNECT_INTERVAL_SECONDS = 6

# --- Logging Setup ---
logger = logging.getLogger("nikki")
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
    logger.addHandler(ch)
logger.setLevel(logging.INFO)


def safe_call(fn: Callable, *args, **kwargs):
    """Call a user callback safely (catch exceptions so client loop isn't affected)"""
    try:
        fn(*args, **kwargs)
    except Exception:
        logger.exception("Callback raised exception")


class NikkiClient:
    """
    Async Nikki client with built-in synchronous thread wrapper, matching Node.js data handling.
    """

    def __init__(self, base_path: Optional[str] = None, auto_reconnect: bool = True):
        self.base_path = base_path or os.getcwd()
        self.auto_reconnect = auto_reconnect
        self.ws_url: Optional[str] = None
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._recv_task: Optional[asyncio.Task] = None
        self._connected_event = asyncio.Event()
        self._stop = False
        self.on_message: Optional[Callable[[Any], None]] = None
        self.on_status: Optional[Callable[[str, dict], None]] = None
        
        # Service configuration details loaded from files
        self._serv_details: Dict[str, str] = {}
        self._token_details: Dict[str, str] = {}
        
        # Sync wrapper attributes
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._thread_loop_running: bool = False
        self._last_send_time: float = 0.0
        self._rate_limit: float = 0.0 # Loaded from service token (in seconds)

    @property
    def is_connected(self) -> bool:
        """
        Robustly checks if the underlying WebSocket connection is currently open.
        This is the recommended way to check the client's status before sending.
        """
        return self._ws is not None and self._ws.state == State.OPEN

    def _read_json_file(self, filename: str) -> dict:
        """Helper to read and parse JSON configuration files."""
        path = os.path.join(self.base_path, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Required file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def build_ws_url(self) -> str:
        """
        Build the ws URL using serviceToken.json and serviceDef.json, and load rate limit.
        Matches Node.js logic by encoding a structure containing both servDef and token.
        """
        token = self._read_json_file(SERVICE_TOKEN_FILE)
        serv_def = self._read_json_file(SERVICE_DEF_FILE)
        
        # Store details required for the outgoing message payload (wsServiceSendDataMsg)
        self._serv_details = {
            'GuID': serv_def.get('GuID', ''),
            'dispName': serv_def.get('dispName', ''),
            'servID': serv_def.get('servID', ''),
            'name': serv_def.get('name', ''),
            'instID': serv_def.get('instID', ''),
        }
        self._token_details = {
            'secrete': token.get('secrete', ''),
            'sessionID': token.get('sessionID', ''),
        }
        
        # Load rate limit from token (defaulting to 0 for no limit if not found)
        self._rate_limit = float(token.get("rateLimit", 0))

        # Use multiple keys for robustness, prioritizing 'wsAddr'
        ws_addr = token.get("wsAddr") or token.get("ws_url") or token.get("wsUrl") or token.get("ws")
        
        if not ws_addr:
            raise ValueError("wsAddr not found in service token file")
        
        # CORRECTION: Match Node.js wsConnectUrlDef structure: {token: {...}, servDef: {...}}
        url_payload = {'token': token, 'servDef': serv_def}
        # Use separators to minify JSON for URL (matching Node.js stringify behavior)
        encoded = quote(json.dumps(url_payload, separators=(",", ":")), safe=':/')
        
        full = f"{ws_addr}?{QUERY_STRING_KEY}={encoded}"
        self.ws_url = full
        return full

    async def connect(self, timeout: Optional[float] = None) -> None:
        """
        Establish websocket connection. This will also spawn the message receive loop.
        """
        if self.is_connected:
             logger.warning("Connection already active.")
             return

        if not self.ws_url:
            self.build_ws_url()
            
        url = self.ws_url
        logger.info("Connecting to %s", url)
        
        try:
            self._ws = await asyncio.wait_for(
                websockets.connect(url, ping_interval=20, ping_timeout=10),
                timeout=timeout
            )
            self._connected_event.set()
            logger.info("Connected")
            if self.on_status:
                safe_call(self.on_status, "connected", {"url": url})
            
            self._recv_task = asyncio.create_task(self._receive_loop())
            
        except Exception as e:
            logger.error("Failed to connect: %s", e)
            if self.on_status:
                safe_call(self.on_status, "error", {"error": str(e)})
            self._connected_event.clear()
            
            if self.auto_reconnect and not self._stop:
                logger.info("Reconnecting in %s seconds...", RECONNECT_INTERVAL_SECONDS)
                await asyncio.sleep(RECONNECT_INTERVAL_SECONDS)
                await self.connect(timeout=timeout)

    async def _receive_loop(self):
        """
        Asynchronously waits for and processes incoming messages, implementing Node.js unwrapping.
        """
        assert self._ws is not None
        try:
            async for raw in self._ws:
                try:
                    data = json.loads(raw)
                    
                    # Node.js Data Unwrapping Logic: Check structure (data.action == 'sendMessage')
                    if (isinstance(data, dict) and 
                        data.get('action') == 'sendMessage' and 
                        isinstance(data.get('data'), dict) and
                        data['data'].get('data') is not None):
                        
                        # Extract the final payload: equivalent to data.data.data
                        final_payload = data['data']['data']
                        logger.debug("Unwrapped payload for on_message: %s", final_payload)
                        if self.on_message:
                            safe_call(self.on_message, final_payload)
                    else:
                        logger.warning("Received message did not match expected 'sendMessage' structure: %s", data)
                        # Fallback: still pass the raw JSON data to the callback if not unwrapped
                        if self.on_message:
                            safe_call(self.on_message, data)
                            
                except json.JSONDecodeError:
                    # If not valid JSON, treat as raw data
                    logger.debug("Received raw data: %s", raw)
                    if self.on_message:
                        safe_call(self.on_message, raw)
                except Exception as e:
                    logger.exception(f"Error processing received message: {e}")
                    
        except websockets.ConnectionClosed as cc:
            logger.warning("Websocket closed: %s", cc)
            self._connected_event.clear()
            if self.on_status:
                safe_call(self.on_status, "disconnected", {"reason": str(cc)})
            
            if self.auto_reconnect and not self._stop:
                logger.info("Will attempt reconnect in %s seconds", RECONNECT_INTERVAL_SECONDS)
                await asyncio.sleep(RECONNECT_INTERVAL_SECONDS)
                await self.connect()
                
        except Exception as e:
            logger.exception("Receive loop error: %s", e)
            self._connected_event.clear()
            if self.on_status:
                safe_call(self.on_status, "error", {"error": str(e)})
            
            if self.auto_reconnect and not self._stop:
                await asyncio.sleep(RECONNECT_INTERVAL_SECONDS)
                await self.connect()

    def _get_node_data(self, data: Any) -> Optional[Dict[str, Any]]:
        """
        Equivalent to Node.js getNodedata(). Packages user data with service credentials.
        Enforces the OUT_DATA_SIZE_SEGMENT_MAX_LIMIT check on the *input* data.
        """
        if not data:
            logger.error('Invalid input: send some valid data.')
            return None

        # Check segment size limit on the input data itself
        try:
            # Use minified JSON for accurate size check
            dt_str = json.dumps(data, separators=(",", ":"), default=str)
        except Exception as e:
            logger.error(f'Exception while serializing input data for segment check: {e}')
            return None

        if len(dt_str) > OUT_DATA_SIZE_SEGMENT_MAX_LIMIT:
            logger.error(f'Input data size is {len(dt_str)}, segment limit exceeded. Should be less than {OUT_DATA_SIZE_SEGMENT_MAX_LIMIT}')
            return None

        # Create the wsServiceSendDataMsg payload structure (equivalent)
        n_data = {
            **self._serv_details, # GuID, dispName, servID, name, instID
            **self._token_details, # secrete, sessionID
            'data': data
        }
        
        # Ensure all required fields were loaded
        if not (self._serv_details and self._token_details):
             logger.error("Service configuration details missing. Cannot package message.")
             return None
             
        return n_data


    async def send(self, data: Any) -> None:
        """
        Send a JSON-serializable object over websocket, implementing full Node.js packaging,
        size limits, and rate limiting.
        """
        if not self.is_connected: # Use the robust connection check
            raise RuntimeError("Websocket is not connected")
        
        # Rate limiting check (Node.js check: timeDiff > (rateLimit * 1000))
        time_elapsed = time.time() - self._last_send_time
        rate_limit_seconds = self._rate_limit
        
        if rate_limit_seconds > 0 and time_elapsed < rate_limit_seconds:
            # Note: The Node.js code logs an error and returns false. We raise an error for the async function.
            raise RuntimeError(f"Rate limit exceeded ({rate_limit_seconds} seconds/msg). Try again in {rate_limit_seconds - time_elapsed:.2f} seconds.")
            
        # 1. Package the data (Segment Size Check inside)
        srv_data = self._get_node_data(data)
        if srv_data is None:
            # _get_node_data handles logging for invalid input/segment size
            raise ValueError("Data packaging failed due to size limit or invalid input.")

        # 2. Serialize the full package (Final Size Check)
        # Use separators to minify JSON for accurate size check
        out = json.dumps(srv_data, separators=(",", ":"), default=str)
        
        if len(out) > OUT_DATA_SIZE_MAX_LIMIT:
            logger.error(f"Exceeded outgoing data size. Final payload ({len(out)} > {OUT_DATA_SIZE_MAX_LIMIT} bytes).")
            raise ValueError(f"Exceeded outgoing data size. Final payload is {len(out)} bytes.")
            
        # 3. Send
        await self._ws.send(out)
        self._last_send_time = time.time()
        logger.debug("Sent: %s", out)

    async def disconnect(self) -> None:
        """
        Stops the client, closes the connection gracefully, and cancels the receive task.
        (Thread cleanup moved to sync_disconnect to prevent RuntimeError).
        """
        self._stop = True
        
        if self._recv_task and not self._recv_task.done():
            self._recv_task.cancel()
            
        if self._ws:
            await self._ws.close(code=1000)
            
        self._connected_event.clear()
        
        logger.info("Disconnected")

    # ---- Synchronous wrapper utilities ----
    
    def run_in_thread(self) -> None:
        """
        Start an asyncio event loop in a background thread so user can call sync helpers.
        """
        if self._thread_loop_running:
            return
            
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        
        while not self._thread_loop_running:
            time.sleep(0.01)
        logger.info("Background thread loop started.")

    def _run_loop(self):
        """The target function for the background thread."""
        asyncio.set_event_loop(self._loop)
        self._thread_loop_running = True
        self._loop.run_forever()

    def _sync_run(self, coro: Awaitable, timeout: Optional[float] = 10.0) -> Any:
        """Helper to run a coroutine from the sync thread."""
        if not self._loop or not self._thread_loop_running:
            raise RuntimeError("Event loop not running. Call run_in_thread() first.")
        
        fut = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return fut.result(timeout=timeout)

    def sync_connect(self, timeout: Optional[float] = 10.0) -> None:
        """Connect synchronously (requires run_in_thread to be called first)"""
        self._sync_run(self.connect(timeout=timeout), timeout=timeout + 5)
        
    def sync_send(self, data: Any, timeout: Optional[float] = 10.0) -> None:
        """Send data synchronously."""
        self._sync_run(self.send(data), timeout=timeout)

    def sync_disconnect(self, timeout: Optional[float] = 10.0) -> None:
        """
        Disconnect synchronously. Runs the async disconnect, then cleanly stops 
        and joins the background thread from the main thread. (FIX for RuntimeError)
        """
        if not self._loop or not self._thread_loop_running:
             logger.warning("Attempted sync_disconnect when not running in thread.")
             return

        # 1. Run the async disconnect coroutine on the background thread
        fut = asyncio.run_coroutine_threadsafe(self.disconnect(), self._loop)
        try:
            fut.result(timeout=timeout)
        except Exception:
             pass # Ignore exceptions during the async disconnect call
        
        # 2. Stop and join the background thread from the main thread (FIX)
        if self._thread and self._thread.is_alive() and self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._thread.join(timeout=5)
            self._thread_loop_running = False
        
        # Clear loop reference since the thread is dead
        self._loop = None
        self._thread = None


# --- Example Usage ---

# Define the callbacks for the example
def on_message_callback(data: Any):
    logger.info("<< MESSAGE RECEIVED >>: %s", data)

def on_status_callback(status: str, detail: dict):
    logger.info("<< STATUS UPDATE >>: %s | Details: %s", status.upper(), detail)

async def async_example():
    logger.info("-" * 40)
    logger.info("STARTING ASYNC EXAMPLE")
    
    client = NikkiClient(auto_reconnect=False) 
    client.on_message = on_message_callback
    client.on_status = on_status_callback

    # 1. Connect
    await client.connect(timeout=5)

    if client.is_connected:
        # 2. Send Data
        logger.info("Async Client sending message 1...")
        await client.send({"async_count": 1, "note": "Initial connection test"})
        await asyncio.sleep(client._rate_limit + 1) # Wait past rate limit

        logger.info("Async Client sending message 2...")
        await client.send({"async_count": 2, "note": "Second test message"})
        
        # 3. Wait to receive (if connecting to a live echo server)
        await asyncio.sleep(2) 
        
    # 4. Disconnect
    await client.disconnect()
    logger.info("ASYNC EXAMPLE COMPLETE")


def sync_example():
    logger.info("-" * 40)
    logger.info("STARTING SYNC EXAMPLE")

    client = NikkiClient(auto_reconnect=False)
    client.on_message = on_message_callback
    client.on_status = on_status_callback
    
    # 1. Start the background loop thread
    client.run_in_thread()
    
    # 2. Connect synchronously
    try:
        client.sync_connect(timeout=5)
        time.sleep(12) 

    except Exception as e:
        logger.error(f"Sync connect failed: {e}")
        # Only disconnect if the thread was successfully started
        if client._thread_loop_running:
             client.sync_disconnect()
        return
    
    # 3. Send Data synchronously
    if client.is_connected:
        try:
            logger.info("Sync Client sending message 1...")
            client.sync_send({"sync_count": 1, "note": "Sync initial test"})
            time.sleep(client._rate_limit + 1) # Wait past rate limit

            logger.info("Sync Client sending message 2...")
            client.sync_send({"sync_count": 2, "note": "Sync second test"})
            
            logger.info("Sync Client sending message 3...")
            client.sync_send({"sync_count": 3, "note": "Sync second test"})
            
            # 4. Wait for a moment to allow async loop to receive (if connecting to a live echo server)
            time.sleep(2) 
        except Exception as e:
            logger.error(f"Sync send failed: {e}")

    # 5. Disconnect synchronously
    client.sync_disconnect()
    logger.info("SYNC EXAMPLE COMPLETE")


def setup_mock_files():
    """Create mock config files for runnable example."""
    mock_service_def = {
        "GuID": "A1B2C3D4-E5F6-7890-1234-567890ABCDEF",
        "servID": "DEV-001",
        "instID": "INST-WEB-001",
        "name": "TestService",
        "dispName": "My Python Client"
    }
    mock_service_token = {
        "sessionID": "sess-xyz-123",
        "secrete": "super-secret-key",
        # Using a reliable public echo server for demonstration
        "wsAddr": "ws://echo.websocket.org", 
        "rateLimit": 2, # 1 message every 2 seconds
        "desc": "A Python client library."
    }

    with open(SERVICE_DEF_FILE, 'w') as f:
        json.dump(mock_service_def, f)
    with open(SERVICE_TOKEN_FILE, 'w') as f:
        json.dump(mock_service_token, f)
        
def cleanup_mock_files():
    """Remove mock config files."""
    for filename in [SERVICE_DEF_FILE, SERVICE_TOKEN_FILE]:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    # setup_mock_files()
    
    sync_example()
    
    # Give the thread time to cleanly shut down before running async
    time.sleep(1) 
    
    try:
        # The main entry point for running async code
        asyncio.run(async_example())
    except Exception as e:
        logger.error(f"Async example failed: {e}")
    
    # cleanup_mock_files()
    logger.info("-" * 40)
    logger.info("All examples finished.")
