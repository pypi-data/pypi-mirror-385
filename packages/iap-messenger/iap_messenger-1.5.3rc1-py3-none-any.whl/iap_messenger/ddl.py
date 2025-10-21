import gc
import time
import zmq
import multiprocessing
import logging

LOGGER = logging.getLogger(__name__)

class DDL:
    """
    DDL (Data Distribution Layer) class using PyZMQ for client-server communication
    to store and retrieve byte data based on UIDs.
    """
    def __init__(self, host: str = "*", port: int = 5555):
        """
        Initializes the DDL service with ZMQ context and server socket.

        Args:
            host (str): The host address to bind the server socket. Default is "*", which binds to all interfaces.
            port (int): The port number for communication. Default is 5555.
        """
        self.manager = multiprocessing.Manager()
        self.datastore = self.manager.dict()
        
        self.server_address = f"tcp://*:{port}"
        self.address = f"{host}:{port}"
        self.host = host
        self.port = port
        
        self._stop_event = multiprocessing.Event()
        self.server_process: multiprocessing.Process | None = None
        self.cleanup_process: multiprocessing.Process | None = None

    def store_data_in_datastore(self, uid: str, data: bytes) -> None:
        """
        Stores byte data in the DDL's in-memory datastore.
        This is typically called on the instance that will run the server
        or an instance that shares the datastore dict.

        Args:
            uid (str): The unique identifier for the data.
            data (bytes): The byte data to store.
        """
        self.datastore[uid] = {"data": data, "timestamp": time.time(), "size": len(data), "status": "stored"}
        LOGGER.debug(f"Data stored in local datastore for UID: {uid} (size: {len(data)} bytes)")

    def _server_loop(self, datastore, stop_event, server_address) -> None:
        """
        The main loop for the server. Listens for requests and responds.
        This method is intended to be run in a separate process.
        """
        # Create ZMQ context and socket within the process
        context = zmq.Context()
        server_socket = context.socket(zmq.REP)
        server_socket.bind(server_address)
        
        poller = zmq.Poller()
        poller.register(server_socket, zmq.POLLIN)

        while not stop_event.is_set():
            try:
                # Poll for incoming messages with a timeout to allow checking stop_event
                polled_socks = poller.poll(timeout=10000)  # 10 second timeout
                socks = {sock: event for sock, event in polled_socks}
                if server_socket in socks and socks[server_socket] == zmq.POLLIN:
                    uid_request = server_socket.recv_string()
                    LOGGER.debug(f"Server received request for UID: '{uid_request}'")

                    if uid_request in datastore:
                        data_entry = datastore[uid_request]
                        data_to_send = data_entry["data"]
                        if not isinstance(data_to_send, bytes):
                            error_message = f"ERROR: Data for UID '{uid_request}' is not bytes."
                            LOGGER.error(error_message)
                            server_socket.send(b'\x01' + error_message.encode('utf-8'))
                            continue
                        
                        server_socket.send(b'\x00' + data_to_send)
                        LOGGER.debug(f"Server sent data for UID: '{uid_request}' (size: {len(data_to_send)} bytes)")
                        datastore[uid_request] = dict(datastore[uid_request])  # Copy to modify
                        datastore[uid_request]["status"] = "sent"
                        datastore[uid_request]["timestamp"] = time.time()
                    else:
                        error_message = f"ERROR: UID '{uid_request}' not found in datastore."
                        server_socket.send(b'\x01' + error_message.encode('utf-8'))
                        LOGGER.warning(f"Server: UID '{uid_request}' not found.")
                else:
                    if stop_event.is_set():
                        LOGGER.info("Server loop: Stop event set, exiting loop.")
                        break
            except zmq.error.ContextTerminated:
                LOGGER.info("Server loop: ZMQ Context terminated, stopping.")
                break
            except zmq.error.ZMQError as e:
                if e.errno == zmq.ETERM:
                    LOGGER.info("Server loop: ZMQ Context terminated, stopping.")
                    break
                else:
                    LOGGER.error(f"ZMQ error in server loop: {e}", exc_info=True)
                    try:
                        server_socket.send(b'\x01' + "ERROR: Server encountered a ZMQ issue.".encode('utf-8'))
                    except zmq.error.ZMQError as zmq_e:
                        LOGGER.error(f"Server error: Could not send error reply: {zmq_e}")

            except Exception as e:
                LOGGER.error(f"Server error: {e}", exc_info=True)
                try:
                    if not server_socket.closed:
                         server_socket.send(b'\x01' + "ERROR: Server encountered an internal issue.".encode('utf-8'))
                except zmq.error.ZMQError as zmq_e:
                    LOGGER.error(f"Server error: Could not send error reply: {zmq_e}")
                break # Exit loop on unexpected errors

        # Clean up ZMQ resources
        server_socket.close()
        context.term()
        LOGGER.info("DDL Server loop has stopped.")

    def _cleanup_loop(self, datastore, stop_event) -> None:
        """
        Periodically cleans up old data from the datastore.
        - Sent data older than 2 minutes is removed.
        - Stored data older than 1 day is removed.
        Runs every 30 seconds.
        """
        CLEANUP_INTERVAL_SECONDS = 30
        SENT_DATA_EXPIRY_SECONDS = 1 * 60  # 1 minutes
        STORED_DATA_EXPIRY_SECONDS = 24 * 60 * 60  # 1 day

        LOGGER.debug("DDL Cleanup loop started.")
        while not stop_event.is_set():
            try:
                # Wait for the interval, or until stop_event is set
                if stop_event.wait(CLEANUP_INTERVAL_SECONDS):
                    break  # Stop event was set, exit loop

                now = time.time()
                keys_to_delete = []

                # Iterate over a snapshot of keys to avoid issues with dict modification
                current_keys = list(datastore.keys())
                for uid in current_keys:
                    entry = datastore.get(uid)  # Re-fetch, entry might be gone
                    if not entry:
                        continue

                    status = entry.get("status")
                    timestamp = entry.get("timestamp")

                    if not isinstance(timestamp, (float, int)):
                        LOGGER.warning(f"Cleanup: UID {uid} has invalid or missing timestamp '{timestamp}'. Skipping.")
                        continue

                    if status == "sent":
                        if (now - timestamp) > SENT_DATA_EXPIRY_SECONDS:
                            keys_to_delete.append(uid)
                            LOGGER.debug(f"Cleanup: Marking sent UID {uid} for deletion (age: {now - timestamp:.0f}s).")
                    elif status == "stored":
                        if (now - timestamp) > STORED_DATA_EXPIRY_SECONDS:
                            keys_to_delete.append(uid)
                            LOGGER.debug(f"Cleanup: Marking stored UID {uid} for deletion (age: {now - timestamp:.0f}s).")
                
                if keys_to_delete:
                    LOGGER.debug(f"Cleanup: Attempting to delete {len(keys_to_delete)} expired entries.")
                    deleted_count = 0
                    for uid_del in keys_to_delete:
                        if uid_del in datastore:  # Final check before deletion
                            try:
                                del datastore[uid_del]
                                LOGGER.debug(f"Cleanup: Successfully deleted UID {uid_del}.")
                                deleted_count +=1
                            except KeyError:
                                # Should not happen if uid_del in datastore was true, but good to be defensive
                                LOGGER.warning(f"Cleanup: UID {uid_del} was removed concurrently before explicit deletion.")
                    if deleted_count > 0:
                        gc.collect()  # Suggest garbage collection after deletions
                        LOGGER.debug(f"Cleanup: Deleted {deleted_count} entries. Suggested GC.")

            except Exception as e:
                LOGGER.error(f"Error in DDL cleanup loop: {e}", exc_info=True)
                # Avoid tight loop on persistent errors if stop event is not set
                if not stop_event.is_set():
                    time.sleep(5) # Wait 5 seconds before next attempt after an error
            
        LOGGER.info("DDL Cleanup loop has stopped.")

    def start_server(self) -> None:
        """
        Starts the DDL server and the cleanup service in new daemon processes.
        If they are already running, this method does nothing.
        """
        needs_server_start = self.server_process is None or not self.server_process.is_alive()
        needs_cleanup_start = self.cleanup_process is None or not self.cleanup_process.is_alive()

        if needs_server_start or needs_cleanup_start:
            self._stop_event.clear()  # Clear the stop signal if we are starting any service

            if needs_server_start:
                self.server_process = multiprocessing.Process(
                    target=self._server_loop,
                    args=(self.datastore, self._stop_event, self.server_address),
                    daemon=True,
                    name="DDLServerProcess"
                )
                self.server_process.start()
                LOGGER.info("DDL Server process started.")
            else:
                LOGGER.info("DDL Server is already running.")

            if needs_cleanup_start:
                self.cleanup_process = multiprocessing.Process(
                    target=self._cleanup_loop,
                    args=(self.datastore, self._stop_event),
                    daemon=True,
                    name="DDLCleanupProcess"
                )
                self.cleanup_process.start()
                LOGGER.info("DDL Cleanup process started.")
            else:
                LOGGER.info("DDL Cleanup process is already running.")
        else:
            LOGGER.info("DDL Server and Cleanup services are already running.")

    def stop_server(self) -> None:
        """
        Signals the server and cleanup processes to stop and waits for them to join.
        """
        server_process_exists_and_is_alive = self.server_process and self.server_process.is_alive()
        cleanup_process_exists_and_is_alive = self.cleanup_process and self.cleanup_process.is_alive()

        if server_process_exists_and_is_alive or cleanup_process_exists_and_is_alive:
            LOGGER.info("Stopping DDL services (Server and/or Cleanup)...")
            self._stop_event.set()

            if server_process_exists_and_is_alive and self.server_process is not None:
                self.server_process.join(timeout=5)
                if self.server_process.is_alive():
                    LOGGER.warning("DDL Server process did not stop in time, terminating...")
                    self.server_process.terminate()
                    self.server_process.join(timeout=2)
                    if self.server_process.is_alive():
                        LOGGER.error("DDL Server process still alive after termination")
                else:
                    LOGGER.info("DDL Server process stopped successfully.")
            
            if cleanup_process_exists_and_is_alive and self.cleanup_process is not None:
                self.cleanup_process.join(timeout=5)
                if self.cleanup_process.is_alive():
                    LOGGER.warning("DDL Cleanup process did not stop in time, terminating...")
                    self.cleanup_process.terminate()
                    self.cleanup_process.join(timeout=2)
                    if self.cleanup_process.is_alive():
                        LOGGER.error("DDL Cleanup process still alive after termination")
                else:
                    LOGGER.info("DDL Cleanup process stopped successfully.")
        else:
            LOGGER.info("DDL services (Server and Cleanup) are not running or processes already stopped.")

    def get_data_from_server(self, uid: str, client: str, timeout_ms: int = 50000) -> tuple[bytes, str | None]:
        """
        Client method to request data from the DDL server.
        A new client socket is created, connected, used, and closed for each call.
        Includes a retry mechanism for network failures.

        Args:
            uid (str): The UID of the data to retrieve.
            client (str): The address (e.g., "localhost:5555" or "tcp://localhost:5555")
                                  for the client socket to connect to.
            timeout_ms (int): Timeout in milliseconds for each request attempt.

        Returns:
            tuple[bytes | None, str | None]: A tuple (data, error_message).
            - If data is found: (data_bytes, None)
            - If error (UID not found, timeout after retries, etc.): (None, error_string)
        """
        client_address = f"tcp://{client}" if not client.startswith("tcp://") else client
        if not uid:
            error_msg = "Client UID cannot be empty."
            LOGGER.error(error_msg)
            return b"", error_msg
        if not client_address: # Technically, client (input) would be empty, leading to "tcp://"
            error_msg = "Client address cannot be empty."
            LOGGER.error(error_msg)
            return b"", error_msg
        
        LOGGER.debug(f"Client attempting to connect to {client_address} for UID: '{uid}' (max_retries=10)")

        max_retries = 10
        base_retry_wait_seconds = 0.2  # Initial wait time, increases with each retry
        last_error_message: str = f"Max retries ({max_retries}) reached for UID '{uid}'."

        # Create ZMQ context for client operations
        client_context = zmq.Context()
        
        try:
            for attempt in range(max_retries):
                client_socket = None
                LOGGER.debug(f"Attempt {attempt + 1}/{max_retries} to get UID '{uid}' from {client_address}")
                try:
                    client_socket = client_context.socket(zmq.REQ)
                    client_socket.setsockopt(zmq.LINGER, 0)
                    client_socket.connect(client_address)
                    LOGGER.debug(f"Client socket (attempt {attempt+1}) connected to {client_address}")

                    poller = zmq.Poller()
                    poller.register(client_socket, zmq.POLLIN)

                    # Send non-blocking to avoid indefinite wait if server is slow to accept
                    # However, REQ socket send is typically blocking until accepted or error.
                    # For true non-blocking send, one might need different patterns or flags,
                    # but for REQ/REP, send itself can block. Here, we assume it's okay.
                    client_socket.send_string(uid) # Removed zmq.NOBLOCK as it's not standard for REQ send.

                    socks = dict(poller.poll(timeout=timeout_ms))
                    if client_socket in socks and socks[client_socket] == zmq.POLLIN:
                        t0 = time.time()
                        response = client_socket.recv()
                        elapsed_time = (time.time() - t0) * 1000
                        LOGGER.debug(f"Client (attempt {attempt+1}) received response in {elapsed_time:.2f} ms for UID: '{uid}' (size: {len(response)} bytes)")

                        if not response:
                            last_error_message = f"Client (attempt {attempt + 1}/{max_retries}) received empty response for UID '{uid}' from {client_address}."
                            LOGGER.warning(last_error_message)
                            if attempt < max_retries - 1:
                                wait_time = base_retry_wait_seconds * (attempt + 1)
                                LOGGER.info(f"Waiting {wait_time:.2f}s before next retry for empty response...")
                                time.sleep(wait_time)
                                continue # Go to next retry attempt
                            else: # This was the last attempt
                                return b"", last_error_message
                        
                        status_byte = response[0:1]
                        payload = response[1:]

                        if status_byte == b'\x01': # Error from server
                            try:
                                error_message_from_server = payload.decode('utf-8')
                                LOGGER.warning(f"Client (attempt {attempt+1}) received server error for UID '{uid}': {error_message_from_server}")
                                return b"", error_message_from_server # Server error, do not retry
                            except UnicodeDecodeError:
                                malformed_error_msg = f"Client (attempt {attempt+1}) received malformed error message (not UTF-8) for UID '{uid}' from server."
                                LOGGER.error(malformed_error_msg)
                                return b"", malformed_error_msg # Malformed server error, do not retry
                        elif status_byte == b'\x00': # Success from server
                            LOGGER.debug(f"Client (attempt {attempt+1}) successfully received data payload for UID: '{uid}' (size: {len(payload)} bytes)")
                            return payload, None # Success
                        else: # Unknown status byte
                            unknown_status_msg = f"Client (attempt {attempt+1}) received response with unknown status byte ({status_byte.hex() if status_byte else 'N/A'}) for UID '{uid}'."
                            LOGGER.error(unknown_status_msg)
                            # Treat as a non-retryable error as it indicates a protocol mismatch
                            return b"", unknown_status_msg
                    else:  # Timeout for this attempt
                        last_error_message = f"Client timeout (attempt {attempt + 1}/{max_retries}) for UID '{uid}' from {client_address} after {timeout_ms}ms."
                        LOGGER.warning(last_error_message)
                        if attempt < max_retries - 1:
                            wait_time = base_retry_wait_seconds * (attempt + 1)
                            LOGGER.info(f"Waiting {wait_time:.2f}s before next retry...")
                            time.sleep(wait_time)
                            continue # Go to next retry attempt
                        else: # This was the last attempt
                            return b"", last_error_message

                except zmq.error.ZMQError as e:
                    last_error_message = f"Client ZMQError (attempt {attempt + 1}/{max_retries}) while requesting UID '{uid}' from {client_address}: {e}"
                    LOGGER.error(last_error_message, exc_info=True)
                    if attempt < max_retries - 1:
                        wait_time = base_retry_wait_seconds * (attempt + 1)
                        LOGGER.info(f"Waiting {wait_time:.2f}s before next retry...")
                        time.sleep(wait_time)
                        continue # Go to next retry attempt
                    else: # This was the last attempt
                        return b"", last_error_message
                except Exception as e:  # Catch any other unexpected errors (non-retryable)
                    error_msg = f"Client general exception (attempt {attempt + 1}/{max_retries}) while requesting UID '{uid}' from {client_address}: {e}"
                    LOGGER.error(error_msg, exc_info=True)
                    return b"", error_msg # Non-retryable general exception
                finally:
                    if client_socket and not client_socket.closed:
                        client_socket.close()
                        LOGGER.debug(f"Client socket (attempt {attempt+1}) to {client_address} closed.")
        finally:
            # Clean up the client context
            client_context.term()
        
        # If loop finishes, all retries were exhausted for retryable errors
        return b"", last_error_message

    def close(self) -> None:
        """
        Stops the server and cleans up multiprocessing resources.
        """
        LOGGER.info("Closing DDL resources...")
        self.stop_server()

        # Close the multiprocessing manager
        if hasattr(self, 'manager'):
            self.manager.shutdown()
            LOGGER.info("Multiprocessing manager shut down.")

if __name__ == '__main__':
    # Basic logging setup for the example
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s')

    LOGGER.info("Starting DDL example...")

    server_host_for_client = "localhost"
    server_port = 5556

    ddl_service = DDL(port=server_port)
    ddl_service.start_server()

    time.sleep(0.5)  # Give server time to start

    client_connect_address = f"tcp://{server_host_for_client}:{server_port}"

    ddl_service.store_data_in_datastore("uid123", b"Hello ZMQ World!")
    ddl_service.store_data_in_datastore("uid456", b"Another piece of data.")

    data, error = ddl_service.get_data_from_server("uid123", client_connect_address)
    if error:
        LOGGER.error(f"Failed to get uid123: {error}")
    else:
        LOGGER.info(f"Got data for uid123: {data.decode() if data else 'None'}")

    data, error = ddl_service.get_data_from_server("uid456", client_connect_address)
    if error:
        LOGGER.error(f"Failed to get uid456: {error}")
    else:
        LOGGER.info(f"Got data for uid456: {data.decode() if data else 'None'}")

    data, error = ddl_service.get_data_from_server("uid789_nonexistent", client_connect_address)
    if error:
        LOGGER.warning(f"Correctly failed to get uid789_nonexistent: {error}")
    else:
        LOGGER.error(f"Incorrectly got data for uid789_nonexistent: {data.decode() if data else 'None'}")

    LOGGER.info("Testing client timeout (this will take ~2 seconds)...")
    data, error = ddl_service.get_data_from_server("uid_timeout_test", client_connect_address, timeout_ms=2000)
    if error and "timeout" in error.lower():
        LOGGER.info(f"Correctly timed out for uid_timeout_test: {error}")
    elif error:
        LOGGER.error(f"Timeout test failed with an unexpected error: {error}")
    else:
        LOGGER.error(f"Timeout test failed. Expected timeout, but got data: {data.decode() if data else 'None'}")

    LOGGER.info("Shutting down DDL service...")
    ddl_service.close()
    LOGGER.info("DDL example finished.")


