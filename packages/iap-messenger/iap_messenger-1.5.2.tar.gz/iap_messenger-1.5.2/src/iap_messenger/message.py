from dataclasses import dataclass
from copy import deepcopy
import uuid
import logging
from typing import Any
from nats import js
from nats.aio.client import Client
from nats.js.object_store import ObjectStore
import nats.errors as nats_errors
from iap_messenger import decoders
from iap_messenger.encoders import encode
from iap_messenger.ddl import DDL
from iap_messenger.utils import MAX_DATA_SIZE
from dataclasses import field
import urllib.parse

LOGGER = logging.getLogger("iap-messenger")
Error = ValueError | None

@dataclass(kw_only=True)
class Message:
    """Class for keeping track of messages."""
    Raw: bytes
    From: str
    To: str | list[str] | None = None
    Parameters: dict[str, str] = field(default_factory=dict)
    Reply: bytes | Any = None
    error: str | None = None
    decoded: Any = None
    is_decoded: bool = False
    uid: str
    datastore: str
    _link: str = ""
    _source: str = ""
    _content_type: str = "application/json"
    _inputs: dict
    _nc: Client
    _js: js.JetStreamContext
    _error_queue: str = "error"
    _outputs: dict
    _encoders: dict
    _queue: str = "queue"
    _data_store:  ObjectStore
    _ddl: DDL | None = None
    _max_size: int = MAX_DATA_SIZE

    def decode(self, decoder:str|None = None) -> tuple[Any, Error]:
        """Decode the Raw data."""
        if decoder is None:
            if "_encoder_" in self.Parameters:
                decoder = self.Parameters["_encoder_"]

        if not decoder:
            decoder = self._content_type

        self.decoded = None
        self.is_decoded = False
        if decoder == "multimodal" or decoder == "multipart":
            # Handle boundary detection if not in content_type
            if "boundary" not in decoder:
                boundary = decoders._get_boundary(self.Raw)
                LOGGER.info(f"Detected boundary: '{boundary}'")
                if boundary:
                    decoder = f"multipart/form-data; boundary={boundary}"
                else:
                    LOGGER.error("Could not detect boundary in multipart data")
                    self.decoded = None
                    self.is_decoded = False
                    return None, ValueError("Could not detect boundary in multipart data")
            
            multiparts, error = decoders.decode_multipart(
                self.Raw, decoder, use_lz4=False)
            for key in multiparts.keys():
                LOGGER.info(f"Found field in multipart data: '{key}'")
            items = self._inputs.get("items", [])
            for k in multiparts.keys():
                if not any(item.get("name") == k for item in items):
                    LOGGER.warning(f"Field '{k}' not in configuration items")
                    multiparts.pop(k)
            if error:
                LOGGER.error(f"Error in multipart decoding: {error}")
                return None, error

            result = {}
            for item in self._inputs["items"]:
                item_data = multiparts.get(item["name"])
                if item_data:
                    if item_data.filename:
                        LOGGER.info(f"Field '{item['name']}' is a file with filename '{item_data.filename}' and size {item_data.size} bytes")
                        if "_filename" not in self.Parameters:
                            self.Parameters["_filename"] = item_data.filename
                        self.Parameters[f"_{item['name']}_size"] = str(item_data.size)
                        self.Parameters[f"_filename_{item['name']}"] = item_data.filename
                    result[item["name"]], error = decoders.decode(item_data.data, item["type"])
                    LOGGER.info(f"Decoded item '{item['name']}': {result[item['name']]}")
                    if error:
                        LOGGER.error(f"Error decoding {item['name']}: {error}")
                        return None, error
                else:
                    LOGGER.warning(f"No data found for field {item['name']}")
            self.decoded = result
            self.is_decoded = True
            return result, None
        else:
            data, err = decoders.decode(self.Raw, decoder)
            if err is None:
                self.decoded = data
                self.is_decoded = True
                return data, None
            else:
                LOGGER.error(f"Error decoding data: {err}")
                return None, err

    def encode(self, encoder: str) -> Error:
        """Encode to Raw data."""
        data, type, err = encode(self.Reply, encoder)
        if err is None:
            self.Reply = data
            self._content_type = type
            self.Parameters["_encoder_"] = encoder
            return None
        else:
            LOGGER.error(f"Error encoding data: {err}")
            return err
    
    def copy(self):
        """Return a copy of the message."""
        return self.__copy__()
    
    def _new_msg(self):
        """Create a new instance of the class."""
        msg = type(self)(
            Raw=b"",
            From=self.From,
            To="",
            Parameters=deepcopy(self.Parameters),
            Reply=None,
            error=None,
            decoded=None,
            is_decoded=self.is_decoded,
            uid=self.uid,
            datastore=self.datastore,
            _link=self._link,
            _source=self._source,
            _content_type=self._content_type,
            _inputs=self._inputs,
            _nc=self._nc,
            _js=self._js,
            _error_queue=self._error_queue,
            _outputs=self._outputs,
            _encoders=self._encoders,
            _queue=self._queue,
            _data_store=self._data_store,
            _ddl=self._ddl,
            _max_size=self._max_size
        )
        if "_encoder_" in msg.Parameters:
            del msg.Parameters["_encoder_"]
        return msg
    
    def __copy__(self):
        """Return a copy of the message."""
        msg = self._new_msg()
        msg.Raw = self.Raw
        msg.To = self.To
        msg.Reply = None if self.Reply is None else deepcopy(self.Reply)
        msg.error = self.error
        msg.decoded = None if self.decoded is None else deepcopy(self.decoded),
        return msg
    
    def new_msg(self, reply: bytes | Any = None, to: str | list[str] | None = None):
        """Return a new message."""
        msg = self._new_msg()
        msg.Reply = reply
        msg.To = to
        return msg

    def set_datastore(self, datastore: str) -> Error:
        """Set the datastore for the message > 8Mb.
        Args:
            datastore (str): The datastore to use, either "ddl" or "object_store".
                             Default is "ddl" if DDL is available, otherwise "object_store".
        """
        if self._ddl and datastore == "ddl":
            self.datastore = "ddl"
            return None
        elif datastore == "object_store":
            self.datastore = "object_store"
            return None
        else:
            return ValueError(
                "Datastore must be 'ddl' or 'object_store'. DDL is available: "
                + str(self._ddl is not None)
            )
    def set_max_size(self, max_size: int) -> Error:
        """Set the maximum size of the message.
        Args:
            max_size (int): The maximum size in bytes.
        """
        if max_size <= 0:
            return ValueError("Maximum size must be greater than 0")
        self._max_size = max_size
        return None

    async def send(self, timeout: float = 0) -> Error:
        """Send the message.
        Args:
            timeout (float): Timeout in seconds for sending the message.
            If 0, the message will be sent without waiting for a response.
        Returns:
            Error: Error or None if no error.
                   If there is a timeout, the error will be "Timeout".
                   If there are no responders, the error will be "No responders".
                   For all other errors, the error will be "Error sending message".
        """
        try:
            if self.To is None:
                return ValueError("No recipient")
            if self.error is not None:
                self.To = self._error_queue
            if isinstance(self.To, list):
                for out in self.To:
                    err = await self._send_msg(out, timeout)
                    if err:
                        return err
                return None
            else:
                return await self._send_msg(self.To, timeout)
        except nats_errors.NoRespondersError:
            return ValueError("No responders")
        except nats_errors.TimeoutError:
            return ValueError("Timeout")
        except Exception as e:  # pylint: disable=W0703
            LOGGER.error("Error sending message: %s", str(e), exc_info=True)
            return ValueError("Error sending message")

    async def _send_msg(self, out: str, timeout: float) -> Error:
        source = self._source
        if self.error is None:
            error = ""
        else:
            error = self.error

        breply = "".encode()
        contentType = ""
        if out != self._error_queue:
            link_out = out
            for k, v in self._outputs.items():
                if v.name == out:
                    link_out = k
                    break
            _out = self._queue + "." + link_out + "." + self.uid
            # print("Sending reply to:", _out)
            source = self._outputs[link_out].type
            if self.Reply is not None:
                if isinstance(self.Reply, (bytes, bytearray)):
                    breply = self.Reply
                else:
                    breply, contentType, err = self._encoders[link_out].encode(
                        self.Reply)
                    self.Parameters["_encoder_"] = self._encoders[link_out].conf["type"]
                    LOGGER.debug(f"encoder: {self.Parameters['_encoder_']}")
                    source = contentType
                    if err:
                        _out = self._error_queue + "." + self.uid
                        out = self._error_queue
                        breply = str(err).encode()
                        error = "Error encoding data"
                if out != self._error_queue:
                    if len(breply) > self._max_size:  # default 8MB
                        store_uid = str(uuid.uuid4())
                        bdata = breply
                        if self._ddl and self.datastore == "ddl":
                            self._ddl.store_data_in_datastore(store_uid, bdata)
                            source = "ddl"
                            reply = f"{store_uid}@{self._ddl.address}"
                            breply = reply.encode()
                        else:
                            breply = store_uid.encode()
                            source = "object_store"
                            retries = 0
                            while retries < 5:
                                try:
                                    LOGGER.debug(f"Storing data in object store: {store_uid}")
                                    await self._data_store.put(store_uid, bdata)
                                    LOGGER.debug(f"Data stored in object store: {store_uid}")
                                    break
                                except nats_errors.TimeoutError:
                                    retries += 1
                                    LOGGER.warning(f"Timeout storing data, retry {retries}/5")
                                except Exception as e:  # pylint: disable=W0703
                                    LOGGER.error(
                                        "Error storing data in object store: %s", str(e), exc_info=True)
                                    _out = self._error_queue + "." + self.uid
                                    out = self._error_queue
                                    breply = str(e).encode()
                                    error = "Error storing data in object store"
                            
        else:
            _out = self._error_queue + "." + self.uid
            breply = self.error.encode() if self.error else "".encode()
            source = "json"

        _params = ""
        for k, v in self.Parameters.items():
            if k == "_filename":
                v = urllib.parse.quote_plus(v)
            if len(_params) > 0:
                _params += f",{k}={v}"
            else:
                _params = f"{k}={v}"
        headers = {"ProcessError": error,
                   "ContentType": contentType,
                   "DataSource": source,
                   "Parameters": _params}
        max_retries = 5
        retries = 0
        if out != self._error_queue:
            if timeout > 0:
                while retries < max_retries:
                    try:
                        nc_out = "nc." + _out
                        await self._nc.request(nc_out, breply, timeout=timeout, headers=headers)
                        LOGGER.debug(f"Message sent on nats core to: {_out}")
                        return None
                    except nats_errors.NoRespondersError:
                        return ValueError("No responders")
                    except nats_errors.TimeoutError:
                        retries += 1
                        LOGGER.warning(f"Timeout sending message, retry {retries}/{max_retries} to {_out}")
                        if retries >= max_retries:
                            return ValueError("Timeout")
                    except Exception as e:  # pylint: disable=W0703
                        LOGGER.error(
                            "Error sending message on core NATS: %s", str(e), exc_info=True)
                        return ValueError("Error sending message")
            
            while retries < max_retries:
                try:
                    await self._js.publish(_out, breply, headers=headers)
                    LOGGER.debug(f"Message sent on nats js to: {_out}")
                    return None
                except nats_errors.TimeoutError:
                    retries += 1
                    LOGGER.warning(f"Timeout sending message, retry {retries}/{max_retries} to {_out}")
                    if retries >= max_retries:
                        return ValueError("Timeout")
                except Exception as e:  # pylint: disable=W0703
                    LOGGER.error("Error sending message on core NATS: %s", str(e), exc_info=True)
                return ValueError("Error sending message")
        else:
            while retries < max_retries:
                try:
                    await self._js.publish(_out, breply, headers=headers)
                    break
                except nats_errors.TimeoutError:
                    retries += 1
                    LOGGER.warning(f"Timeout sending message, retry {retries}/{max_retries} to {_out}")
                    if retries >= max_retries:
                        return ValueError("Timeout")
                except Exception as e:
                    LOGGER.error("Error sending message on ERROR queue: %s", str(e), exc_info=True)
                    return ValueError("Error sending message")
        
        return None