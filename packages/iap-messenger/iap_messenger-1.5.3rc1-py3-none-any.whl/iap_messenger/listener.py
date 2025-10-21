"""
IA Parc Inference service
Support for inference of IA Parc models
"""
import os
import time
import asyncio
import uuid
from inspect import signature
import logging
import logging.config
import nats
import nats.errors as nats_errors
import json
from iap_messenger.config import Config, PipeInputOutput
from iap_messenger.data_encoder import DataEncoder
from iap_messenger.subscription import BatchSubscription
from iap_messenger.message import Message
from iap_messenger.readme_handler import wait_readme
from iap_messenger.ddl import DDL
from iap_messenger.utils import MAX_DATA_SIZE
import urllib.parse

Error = ValueError | None

LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=LEVEL,
    force=True,
    format="%(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger("iap-messenger")
LOGGER.propagate = True


class MsgListener():
    """
    Inference Listener class
    """

    def __init__(self,
                 callback,
                 decode=False,
                 batch:int=-1,
                 inputs:str = "",
                 outputs:str = "",
                 config_path:str= "/opt/pipeline/pipeline.json",
                 url:str="",
                 queue:str=""
                 ):
        """
        Constructor
        Arguments:
        - callback:     Callback function to proccess data
                        callback(data: Any | list[Any], parameters: Optional[dict])
        Optional arguments:
        - inputs:       Input queue name
        - outputs:      Output queue name
        - decode:       Set wether data should be decoded before calling the callback function (default: True)
        - batch:        Batch size for inference (default: -1)
                        If your model do not support batched input, set batch to 1
                        If set to -1, batch size will be determined by the IAP_BATCH_SIZE
                        environment variable
        - config_path:  Path to config file (default: /opt/pipeline/pipeline.json)
        - url:          Url of inference server (default: None)
                        By default determined by the NATS_URL environment variable,
                        however you can orverride it here
        - queue:        Name of queue (default: None)
                        By default determined by the NATS_QUEUE environment variable,
                        however you can orverride it here
        """
        # Init internal variables
        self.decode = decode
        self.timeout = 0.002
        self.exec_time = 0
        self._subs_in = []
        self._subs_out = []
        self.config = Config(config_path)
        if inputs:
            self.config.input_list = inputs.split(",")
        self.lock = asyncio.Lock()
        self.callback = callback
        sig = signature(callback)
        self.callback_args = sig.parameters
        nb_params = len(self.callback_args)
        if nb_params == 1:
            self.callback_has_parameters = False
        else:
            self.callback_has_parameters = True

        if url:
            self.url = url
        else:
            self.url = os.environ.get("NATS_URL", "nats://nats:4222")
        if queue:
            self.queue = queue.replace("/", "-")
        else:
            self.queue = os.environ.get("NATS_QUEUE", "").replace("/", "-")
            if self.queue == "":
                self.queue = os.environ.get("QUEUE", "iap-messenger").replace("/", "-")
        if batch > 0:
            self.batch = batch
        else:
            self.batch = int(os.environ.get("IAP_BATCH_SIZE", -1))
            if self.batch == -1:
                self.batch = int(os.environ.get("BATCH_SIZE", 1))
        if self.batch > 1:
            self.is_batch = True
        else:
            self.is_batch = False
        
        pod_ip = os.environ.get("POD_IP", "")
        zmq_port = int(os.environ.get("ZMQ_PORT", 5555))
        if pod_ip:
            self.ddl = DDL(host=pod_ip, port=zmq_port)
            self.ddl.start_server()
        else:
            self.ddl = None

        self.error_queue = self.queue + ".ERROR"
        self.parameters = {}
        self.inputs: dict[str, PipeInputOutput] =  self.config.Inputs
        self.outputs: dict[str, PipeInputOutput] = self.config.Outputs
        self.encoders: dict[str, DataEncoder] = self.config.encoders
        if len(self.config.input_list) == 0:
            print("No inputs defined")
            quit(1)
        LOGGER.info(f"Inputs: {self.inputs}")
        LOGGER.info(f"self.config.input_list: {self.config.input_list}")
        for link in self.config.input_list:
            self.parameters[link] = self.inputs[link].parameters
            
    @property
    def inputs_name(self) -> list:
        """ Input property """
        return self.config.input_list

    def run(self):
        """
        Run inference service
        """
        asyncio.run(self.run_async())

    async def run_async(self):
        """ Start listening to NATS messages
        url: NATS server url
        batch_size: batch size
        """
        self.nc = await nats.connect(self.url)
        self.js = self.nc.jetstream()

        for q_name in self.inputs_name:
            q_name = q_name.replace("/", "-")
            #item = self.inputs[q_name]
            queue_in = self.queue + "." + q_name
            print("Listening on queue:", queue_in)
            js_in = await self.js.subscribe(queue_in+".>",
                                            queue=self.queue+"-"+q_name,
                                            stream=self.queue)
                
            self._subs_in.append((q_name, js_in))
            nc_in = await self.nc.subscribe("nc."+queue_in+".*.*", queue=self.queue+"-"+q_name)
            self._subs_in.append((q_name, nc_in))

        pos = os.environ.get('POSITION', '0')
        readme_nc = await self.nc.subscribe(f"nc.{self.queue}.readme-{pos}.*.*", queue=self.queue+"-readme")
        self._subs_in.append(("readme", readme_nc))

        print("Default queue out:", self.config.default_output)
        self.data_store = await self.js.object_store(bucket=self.queue+"-data")

        os.system("touch /tmp/running")
        tasks = []
        for link, sub_in in self._subs_in:
            if link == "readme":
                tasks.append(wait_readme(sub_in, self.send_msg))
            else:
                tasks.append(self.wait_msg(link, sub_in))
        await asyncio.gather(*tasks)
        await self.nc.close()

    async def wait_msg(self, link, sub_in):
        # Fetch and ack messagess from consumer.
        if sub_in.subject[:7] == "_INBOX.":
            subject = sub_in.subject[7:]
            is_js = True
        else:
            subject = sub_in.subject.replace(".*.*", "")
            is_js = False
        if self.is_batch:
            batch_sub = BatchSubscription(sub_in, self.batch)
        while True:
            if not self.is_batch:
                try:
                    msg = await sub_in.next_msg(timeout=600)
                    LOGGER.debug("Single Message received on %s: %s", subject, msg.subject)
                except nats_errors.TimeoutError:
                    continue
                except TimeoutError:
                    continue
                except nats_errors.ConnectionClosedError:
                    LOGGER.error(
                        "Fatal error message handler: ConnectionClosedError")
                    break
                except asyncio.CancelledError:
                    LOGGER.error(
                        "Fatal error message handler: CancelledError")
                    break
                except Exception as e: # pylint: disable=W0703
                    LOGGER.error("Unknown error:", exc_info=True)
                    LOGGER.debug(e)
                    continue
                
                # Message received
                await asyncio.gather(
                    self.term_msg([msg], is_js),
                    self.handle_msg(subject, link, [msg])
                )
            else:
                msgs = []
                try:
                    msgs = await batch_sub.get_batch(self.timeout)
                    LOGGER.debug("Batch of %d messages received on %s", len(msgs), subject)
                except nats_errors.TimeoutError:
                    continue
                except TimeoutError:
                    continue
                except nats_errors.ConnectionClosedError:
                    LOGGER.error(
                        "Fatal error message handler: ConnectionClosedError")
                    break
                except asyncio.CancelledError:
                    LOGGER.error(
                        "Fatal error message handler: CancelledError")
                    break
                
                # Messages received
                t0 = time.time()
                await asyncio.gather(
                    self.term_msg(msgs, is_js),
                    self.handle_msg(subject, link, msgs)
                )
                t1 = time.time()
                if self.exec_time == 0:
                    self.exec_time = t1 - t0
                self.exec_time = (self.exec_time + t1 - t0) / 2
                if self.exec_time < 0.02:
                    self.timeout = 0.002
                elif self.exec_time > 0.35:
                    self.timeout = 0.05
                else:
                    self.timeout = self.exec_time * 0.15

    async def handle_msg(self, subject, link, msgs):
        async with self.lock:
            if self.is_batch:
                results = [await self.get_data(subject, msg, link) for msg in msgs]
                LOGGER.debug("Batch of %d messages processed on %s", len(results), subject)
                iap_msgs = [msg for msg, err in results if msg is not None]
                if len(iap_msgs) == 0:
                    return
                await self._process_data(iap_msgs)
            else:
                for msg in msgs:
                    iap_msg, err = await self.get_data(subject, msg, link)
                    LOGGER.debug("Message processed on %s: %s", subject, iap_msg.uid)
                    if err is not None:
                        LOGGER.error(f"Error getting data: {err}")
                        return
                    await self._process_data([iap_msg])
        return

    async def term_msg(self, msgs, is_js=False):
        if is_js:
            for msg in msgs:
                await msg.ack()
        else:
            ack = "".encode("utf8")
            for msg in msgs:
                await msg.respond(ack)

    async def get_data(self, subject, msg, link) -> tuple[Message, str | None]:
        l_sub = len(subject) + 1
        uid = msg.subject[(l_sub):]
        source = msg.headers.get("DataSource", "")
        params_lst = msg.headers.get("Parameters", "")
        params = {}
        reply_to = self.outputs[self.config.default_output].name
        if self.inputs[link].output is not None:
            reply_to = self.inputs[link].output
        LOGGER.debug("Getting Message data from subject: %s, link: %s, uid: %s, source: %s, reply_to: %s",
                     subject, link, uid, source, reply_to)
        iap_msg = Message(
            Raw=msg.data,
            From=self.inputs[link].name,
            To=reply_to or "",
            Parameters=params,
            Reply=None,
            is_decoded=False,
            uid=uid,
            datastore='object_store',
            _link=link,
            _source=source,
            _inputs=self.inputs[link].data,
            _nc=self.nc,
            _js=self.js,
            _error_queue=self.error_queue,
            _outputs=self.outputs,
            _encoders=self.encoders,
            _queue=self.queue,
            _data_store=self.data_store,
            _ddl=self.ddl
        )
        if self.ddl is not None:
            iap_msg.datastore = "ddl"
        if params_lst:
            for p in params_lst.split(","):
                args = p.split("=")
                if len(args) == 2:
                    k, v = args
                    if v == "None":
                        params[k] = None
                    elif k in self.parameters[link]:
                        if v:
                            if self.parameters[link][k] == "float":
                                params[k] = float(v)
                            elif self.parameters[link][k] == "integer":
                                params[k] = int(v)
                            elif self.parameters[link][k] == "boolean":
                                params[k] = v.lower() in ("yes", "true", "True", "1")
                            elif self.parameters[link][k] == "json":
                                params[k] = json.loads(v)
                            else:
                                params[k] = v
                        else:
                            if self.parameters[link][k] != "string":
                                params[k] = None
                            else:
                                params[k] = ""
                    else:
                        # Unknown parameter
                        if k == "_filename":
                            params[k] = urllib.parse.unquote_plus(v)
                            continue
                        params[k] = v
            iap_msg.Parameters = params
        iap_msg._content_type = msg.headers.get("ContentType", "")
        data = ''.encode()
        if source == "object_store":
            obj_res = await self.data_store.get(msg.data.decode())
            asyncio.create_task(self.data_store.delete(msg.data.decode()))
            if obj_res.data:
                data = obj_res.data
            else:
                LOGGER.error(f"Data not found in object store: {msg.data.decode()}")
                return iap_msg, "Data not found in object store: empty string"
            
        elif source == "ddl":
            if self.ddl is None:
                LOGGER.error("DDL not initialized")
                return iap_msg, "DDL not initialized"
            dest = msg.data.decode()
            if not dest:
                LOGGER.error("Data not found in DDL: empty string")
                return iap_msg, "Data not found in DDL: empty string"
            elts = dest.split("@")
            if len(elts) != 2:
                LOGGER.error(f"Data not found in DDL: {msg.data.decode()}")
            data, err = self.ddl.get_data_from_server(elts[0], elts[1])
            if err:
                LOGGER.error(f"Error getting data from DDL: {err}")
                
        else:
            if isinstance(msg.data, bytes):
                data = msg.data
            else:
                data = str(msg.data).encode()
        iap_msg.Raw = data

        return iap_msg, None

    async def send_msg(self, out, uid, source, data, parameters={}, error=""):
        if error is None:
            error = ""
        _params = ""
        if parameters and isinstance(parameters, dict):
            for k,v in parameters.items():
                if len(_params) > 0:
                    _params += f",{k}={v}"
                else:
                    _params = f"{k}={v}"
        breply = "".encode()
        contentType = ""
        if out != self.error_queue:
            link_out = out
            for k, v in self.outputs.items():
                if v.name == out:
                    link_out = k
                    break
            _out = self.queue + "." + link_out + "." + uid
            #print("Sending reply to:", _out)
            if data is not None:
                if isinstance(data, (bytes, bytearray)):
                    breply = data
                else:
                    breply, contentType, err = self.encoders[link_out].encode(data)
                    if err:
                        _out = self.error_queue + "." + uid
                        out = self.error_queue
                        breply = str(err).encode()
                        error = "Error encoding data"
                if out != self.error_queue:
                    if len(breply) > MAX_DATA_SIZE: # 8MB
                        store_uid = str(uuid.uuid4())
                        source = "object_store"
                        bdata = breply
                        breply = store_uid.encode()
                        retries = 0
                        while retries < 5:
                            try:
                                LOGGER.debug(
                                    f"Storing data in object store: {store_uid}")
                                await self.data_store.put(store_uid, bdata)
                                LOGGER.debug(
                                    f"Data stored in object store: {store_uid}")
                                break
                            except nats_errors.TimeoutError:
                                retries += 1
                                LOGGER.warning(
                                    f"Timeout storing data, retry {retries}/5")
                            except Exception as e:  # pylint: disable=W0703
                                LOGGER.error(
                                    "Error storing data in object store: %s", str(e), exc_info=True)
                                _out = self.error_queue + "." + uid
                                out = self.error_queue
                                breply = str(e).encode()
                                error = "Error storing data in object store"
        else:
            _out = self.error_queue + "." + uid
            breply = data.encode()
        
        headers = {"ProcessError": error,
                   "ContentType": contentType,
                   "DataSource": source,
                   "Parameters": _params}
        max_retries = 5
        retries = 0
        if out != self.error_queue:
            while retries < max_retries:
                try:
                    nc_out = "nc." + _out
                    await self.nc.request(nc_out, breply, timeout=60, headers=headers)
                    _sent = True
                    break
                except nats_errors.TimeoutError:
                    retries += 1
                    LOGGER.warning(f"Timeout sending message, retry {retries}/{max_retries} to {_out}")
                    if retries >= max_retries:
                        return ValueError("Timeout")
                except nats_errors.NoRespondersError:
                    await self.js.publish(_out, breply, headers=headers)
                except Exception as e: # pylint: disable=W0703
                    LOGGER.error("Error sending message on core NATS:", exc_info=True)
                    LOGGER.debug(e)
        else:
            while retries < max_retries:
                try:
                    await self.js.publish(_out, breply, headers=headers)
                    break
                except nats_errors.TimeoutError:
                    retries += 1
                    LOGGER.warning(
                        f"Timeout sending message, retry {retries}/{max_retries} to {_out}")
                    if retries >= max_retries:
                        return ValueError("Timeout")
                except Exception as e:
                    LOGGER.error(
                        "Error sending message on ERROR queue: %s", str(e), exc_info=True)
                    return ValueError("Error sending message")

    async def _process_data(self, msgs: list[Message]):
        """
        Process data
        Arguments:
        - requests:   list of data to process
        - is_batch:   is batched data
        """
        LOGGER.debug("handle request")
        has_data = False
        _uids = []
        if len(msgs) == 0:
            return
        for msg in msgs:
            _uids.append(msg.uid)
            if self.decode:
                data, error = msg.decode()
                if error:
                    msg.error = str(error)
                    asyncio.create_task(msg.send())
                    continue
                else:
                    msg.is_decoded = True
                    msg.decoded = data
                    has_data = True
            elif len(msg.Raw) > 0:
                has_data = True
        
        try_error = ""
        if has_data:
            try:
                error = ""
                if self.is_batch:
                    result = self.callback(msgs)
                    if result is None:
                        return
                    if not isinstance(result, list):
                        error = "batch reply is not a list"
                    if len(msgs) != len(result):
                        error = "batch reply has wrong size"
                    if error:
                        for msg in msgs:
                            msg.error = error
                            asyncio.create_task(msg.send())
                        return
                    
                    for i, reply in enumerate(result):
                        uid = self.return_reply(msgs[i], reply)
                        _uids.remove(uid)
                    # Handle remaining messages
                    for uid in _uids:
                        for msg in msgs:
                            if msg.uid == uid:
                                msg.error = "failed to process data"
                                asyncio.create_task(msg.send())
                else:
                    result = self.callback(msgs[0])
                    if result is None:
                        return
                    self.return_reply(msgs[0], result)
                
            except ValueError:
                LOGGER.error("Fatal error message handler", exc_info=True)
                try_error  = "Wrong input"
            except Exception as e: # pylint: disable=W0703
                LOGGER.error("Fatal error message handler", exc_info=True)
                try_error = f'Fatal error: {str(e)}'
            if try_error:
                for msg in msgs:
                    asyncio.create_task(self.send_msg(
                        self.error_queue, msg.uid, msg._source, try_error, msg.Parameters, "Wrong input"))

    def return_reply(self, request: Message, reply) -> str:
        """
        Return message
        Arguments:
        - msg:   Message to return
        """
        uid = ""
        if isinstance(reply, Message):
            if reply.To is None:
                return request.uid
            if not uid:
                uid = reply.uid
            if reply.error:
                asyncio.create_task(self.async_send_msg(reply))
                return uid
            else:
                asyncio.create_task(self.async_send_msg(reply))
                return uid

        elif isinstance(reply, list):
            for _msg in reply:
                if isinstance(_msg, Message):
                    if _msg.To is None:
                        continue
                    if not uid:
                        uid = _msg.uid
                    if _msg.error:
                        asyncio.create_task(self.async_send_msg(_msg))
                        break
                    else:
                        asyncio.create_task(self.async_send_msg(_msg))

                else:
                    #send_args = [request.To, request.uid, request._source, request.Reply, request.Parameters, "reply is not a Message"]
                    request.error = "reply is not a Message"
                    asyncio.create_task(self.async_send_msg(request))
                    return uid
        else:
            #send_args = [request.To, request.uid, request._source, request.Reply, request.Parameters, "reply is not a Message"]
            request.error = "reply is not a Message"
            asyncio.create_task(self.async_send_msg(request))
        return uid

    async def async_send_msg(self, msg: Message):
        await msg.send()
        del msg
        