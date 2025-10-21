import asyncio
import websockets
import websockets.asyncio.client
import logging
import ssl
import json
import time
import datetime
from datetime import timezone
from typing import TypedDict, cast

from .indra_event import IndraEvent
from .indra_time import IndraTime
from .server_config import Profiles, Profile


class IeFutureTable(TypedDict):
    future: asyncio.futures.Future[IndraEvent]
    start_time: float

    
class IndraClient:
    def __init__(
        self,
        profile: Profile | None =None,
        profile_name: str | None ="default",
        verbose: bool =False,
        module_name: str | None =None,
        log_handler: logging.Handler | None =None,
    ):
        self.log: logging.Logger = logging.getLogger("IndraClient")
        if log_handler is not None:
            self.log.addHandler(log_handler)
        if module_name is None:
            self.module_name: str = "IndraClient (python)"
        else:
            self.module_name = module_name
        self.websocket: websockets.asyncio.client.ClientConnection | None = None
        self.verbose: bool = verbose
        self.trx: dict[str, IeFutureTable] = {}
        self.recv_queue: asyncio.Queue[IndraEvent] = asyncio.Queue()
        self.recv_task: asyncio.Task[bool] | None = None
        self.session_id: str | None = None
        self.username: str | None = None
        self.initialized: bool = False
        self.error_shown: bool = False
        self.profiles: Profiles = Profiles()
        self.uri: str | None = None
        if profile is not None:
            self.profiles.check_profile(profile)
        if profile is not None:
            self.profile: Profile|None = profile
            self.initialized = True
        else:
            if profile_name == "default" or profile_name is None:
                self.profile = self.profiles.get_default_profile()
            else:
                self.profile = self.profiles.get_profile(profile_name)
            if self.profile is not None:
                self.initialized = True
            else:
                self.log.error("Failed to load any profile!")

    async def init_connection(self, verbose: bool = False) -> websockets.asyncio.client.ClientConnection | None:
        """Initialize connection"""
        if self.initialized is False:
            self.trx = {}
            self.websocket = None
            self.log.error(
                "Indrajala init_connection(): connection profile data not initialized!"
            )
            return None
        if self.websocket is not None:
            if verbose is True:
                self.log.warning(
                    "Websocket already initialized, please call close_connection() first!"
                )
            return self.websocket
        self.trx = {}
        if self.profile is not None:
            self.uri = Profiles.get_uri(self.profile)
        if self.profile is not None and self.profile["TLS"] is True:
            ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            if 'ca_authority' in self. profile and self.profile["ca_authority"] is not None:
                try:
                    ssl_ctx.load_verify_locations(cafile=self.profile["ca_authority"])
                except Exception as e:
                    self.log.error(
                        f"Could not load CA authority file {self.profile['ca_authority']}: {e}"
                    )
                    self.websocket = None
                    return None
        else:
            ssl_ctx = None
        if self.uri is None:
            self.log.error("URI is None")
            return None
        try:
            self.websocket = await websockets.connect(self.uri, ssl=ssl_ctx)
        except Exception as e:
            self.log.error(f"Could not connect to {self.uri}: {e}")
            self.websocket = None
            return None
        # self.recv_queue.empty()
        self.recv_task = asyncio.create_task(self.fn_recv_task())
        self.session_id = None
        self.username = None
        self.error_shown = False
        return self.websocket

    async def fn_recv_task(self):
        """Receive task"""
        while self.websocket is not None:
            try:
                message_raw = await self.websocket.recv()
                message = str(message_raw)
                if self.verbose is True:
                    self.log.info(f"Received message: {message}")
            except Exception as e:
                self.log.error(f"Could not receive message: {e}, exiting recv_task()")
                self.recv_task = None
                return False
            # ie = IndraEvent()
            ie = IndraEvent.from_json(message)
            if ie.uuid4 in self.trx:
                fRec: IeFutureTable = cast(IeFutureTable, self.trx[ie.uuid4])
                dt: float = time.time() - fRec["start_time"]
                if self.verbose is True:
                    self.log.info(
                        "---------------------------------------------------------------"
                    )
                    self.log.info(
                        f"Future: trx event {ie.to_scope}, uuid: {ie.uuid4}, {ie.data_type}, dt={dt}"
                    )
                ie_fut: asyncio.futures.Future[IndraEvent] = fRec["future"]
                ie_fut.set_result(ie)
                del self.trx[ie.uuid4]
            else:
                if self.verbose is True:
                    self.log.info(
                        f"Received event {ie.to_scope}, uuid: {ie.uuid4}, {ie.data_type}"
                    )
                await self.recv_queue.put(ie)
        self.recv_task = None
        return True

    async def send_event(self, event: IndraEvent):
        """Send event"""
        if self.initialized is False:
            if self.error_shown is False:
                self.error_shown = True
                self.log.error(
                    "Indrajala send_event(): connection data not initialized!"
                )
            return None
        if self.websocket is None:
            self.log.error(
                "Websocket not initialized, please call init_connection() first!"
            )
            return None
#        if isinstance(event, IndraEvent) is False:
#            self.log.error("Please provide an IndraEvent object!")
#            return None
        if event.domain.startswith("$trx/") is True:
            replyEventFuture: asyncio.futures.Future[IndraEvent] | None = asyncio.futures.Future()
            fRec: IeFutureTable = {
                "future": replyEventFuture,
                "start_time": time.time(),
            }
            self.trx[event.uuid4] = fRec
            self.log.debug("Future: ", replyEventFuture)
        else:
            replyEventFuture = None
        try:
            await self.websocket.send(event.to_json())
        except Exception as e:
            self.log.error(f"Could not send message: {e}")
            self.initialized = False
        return replyEventFuture

    async def recv_event(self, timeout: float | None = None):
        """Receive event"""
        if self.initialized is False:
            self.log.error("Indrajala recv_event(): connection data not initialized!")
            return None
        if self.websocket is None:
            self.log.error(
                "Websocket not initialized, please call init_connection() first!"
            )
            return None
        if timeout is None:
            try:
                ie: IndraEvent = await self.recv_queue.get()
            except Exception as e:
                self.log.error(f"Could not receive message: {e}")
                return None
        else:
            try:
                ie = await asyncio.wait_for(self.recv_queue.get(), timeout=timeout)
            except TimeoutError:
                return None
            except Exception as e:
                self.log.warning(f"Timeout receive failed: {e}")
                return None
        self.recv_queue.task_done()
        return ie

    async def close_connection(self):
        """Close connection"""
        if self.initialized is False:
            self.log.error(
                "Indrajala close_connection(): connection data not initialized!"
            )
            return False
        if self.websocket is None:
            self.log.error(
                "Websocket not initialized, please call init_connection() first!"
            )
            return False
        if self.recv_task is not None:
            _ = self.recv_task.cancel()
            self.recv_task = None
        await self.websocket.close()
        self.trx = {}
        self.websocket = None
        self.session_id = None
        self.username = None
        return True

    async def subscribe(self, domains: str | list[str] | None):
        """Subscribe to domain"""
        if self.initialized is False:
            self.log.error("Indrajala subscribe(): connection data not initialized!")
            return False
        if self.websocket is None:
            self.log.error(
                "Websocket not initialized, please call init_connection() first!"
            )
            return False
        if domains is None or domains == "":
            self.log.error("Please provide a valid domain(s)!")
            return False
        ie = IndraEvent()
        ie.domain = "$cmd/subs"
        ie.from_id = "ws/python"
        ie.data_type = "vector/string"
        if self.session_id is not None:
            ie.auth_hash = self.session_id
        if isinstance(domains, list) is True:
            ie.data = json.dumps(domains)
        else:
            ie.data = json.dumps([domains])
        await self.websocket.send(ie.to_json())
        return True

    async def unsubscribe(self, domains: str | list[str] | None):
        """Unsubscribe from domain"""
        if self.initialized is False:
            self.log.error("Indrajala unsubscribe(): connection data not initialized!")
            return False
        if self.websocket is None:
            self.log.error(
                "Websocket not initialized, please call init_connection() first!"
            )
            return False
        if domains is None or domains == "":
            self.log.error("Please provide a valid domain(s)!")
            return False
        ie = IndraEvent()
        ie.domain = "$cmd/unsubs"
        ie.from_id = "ws/python"
        ie.data_type = "vector/string"
        if self.session_id is not None:
            ie.auth_hash = self.session_id
        if isinstance(domains, list) is True:
            ie.data = json.dumps(domains)
        else:
            ie.data = json.dumps([domains])
        await self.websocket.send(ie.to_json())
        return True

    async def get_history(
        self, domain: str | None, start_time: float | None =None, end_time: float | None =None, sample_size: int | None =None, mode: str ="Sample"
    ):
        """Get history of domain

        returns a future object, which will be set when the reply is received
        """
        cmd = {
            "domain": domain,
            "time_jd_start": start_time,
            "time_jd_end": end_time,
            "limit": sample_size,
            # "data_type": "number/float%",
            "mode": mode,
        }
        ie = IndraEvent()
        ie.domain = "$trx/db/req/history"
        ie.from_id = "ws/python"
        ie.data_type = "historyrequest"
        if self.session_id is not None:
            ie.auth_hash = self.session_id
        ie.data = json.dumps(cmd)
        if self.verbose is True:
            self.log.info(f"Sending: {ie.to_json()}")
        return await self.send_event(ie)

    async def get_wait_history(
        self, domain: str | None, start_time: float | None =None, end_time: float | None =None, sample_size: int | None =None, mode: str ="Sample"
    ):
        future = await self.get_history(domain, start_time, end_time, sample_size, mode)
        if future is None:
            return None
        hist_result = await future
        try:
            hist: list[tuple[float, float]] = cast(list[tuple[float,float]], json.loads(hist_result.data))
        except Exception as e:
            self.log.error(f"Failed to parse history: {e}")
            return None
        return hist

    @staticmethod
    def get_current_time_jd():
        cdt = datetime.datetime.now(timezone.utc)
        dt_jd = IndraTime.datetime_to_julian(cdt)
        return dt_jd

    @staticmethod
    async def _get_history_block(
        username: str,
        password: str,
        domain: str | None = None,
        start_time: float | None = None,
        end_time: float | None = None,
        verbose: bool = False,
        sample_size: int = 20,
    ):
        ic = IndraClient(verbose=verbose)
        if verbose is True:
            ic.log.info(f"Connecting")
        _ = await ic.init_connection()
        if verbose is True:
            ic.log.info("Connected to Indrajala")
        ret = await ic.login_wait(username, password)
        if verbose is True:
            ic.log.info(f"Login result: {ret}")
        if ret is not None:
            if verbose is True:
                ic.log.info(f"Logged in as {username}")
            data = await ic.get_wait_history(
                domain=domain,
                start_time=start_time,
                end_time=end_time,
                sample_size=sample_size,
                mode="Sample",
            )
            if verbose is True:
                ic.log.info(f"Data: {data}")
            _ = await ic.logout_wait()
            _ = await ic.close_connection()
            if verbose is True:
                ic.log.info("Logged out and closed connection")
            return data
        return None

    @staticmethod
    def get_history_sync(
        username: str,
        password: str,
        domain: str | None,
        start_time: float | None,
        end_time: float | None = None,
        sample_size: int = 20,
        verbose: bool = False,
    ):
        return asyncio.run(
            IndraClient._get_history_block(
                username, password, domain, start_time, end_time, verbose, sample_size
            )
        )

    async def get_last_event(self, domain: str):
        """Get last event of domain"""
        ie = IndraEvent()
        ie.domain = "$trx/db/req/last"
        ie.from_id = "ws/python"
        ie.data_type = "json/reqlast"
        if self.session_id is not None:
            ie.auth_hash = self.session_id
        ie.data = json.dumps({"domain": domain})
        return await self.send_event(ie)

    async def get_wait_last_event(self, domain: str):
        future = await self.get_last_event(domain)
        if future is None:
            return None
        last_result = await future
        if last_result.data != "":
            return IndraEvent.from_json(last_result.data)
        else:
            return None

    async def get_unique_domains(self, domain: str | None = None, data_type: str | None = None):
        """Get unique domains"""
        if domain is None:
            domain = "$event/measurement%"
        cmd = {}
        cmd["domain"] = domain
        if data_type is not None:
            cmd["data_type"] = data_type
        ie = IndraEvent()
        ie.domain = "$trx/db/req/uniquedomains"
        ie.from_id = "ws/python"
        ie.data_type = "uniquedomainsrequest"
        if self.session_id is not None:
            ie.auth_hash = self.session_id
        ie.data = json.dumps(cmd)
        return await self.send_event(ie)

    async def get_wait_unique_domains(self, domain: str | None = None, data_type: str | None = None) -> list[str] | None:
        future = await self.get_unique_domains(domain, data_type)
        if future is None:
            return None
        domain_result = await future
        try:
            doms: list[str] = cast(list[str], json.loads(domain_result.data))
        except Exception as e:
            self.log.error(f"Failed to parse domain_result: {e}")
            return None
        return doms

    async def delete_recs(self, domains: str | list[str] | None = None, uuid4s: str | list[str] | None = None):
        if domains is None and uuid4s is None:
            self.log.error("Please provide a domain or uuid4s")
            return None
        if domains is not None and uuid4s is not None:
            self.log.error("Please provide either a domain or uuid4s")
            return None
        cmd = {
            "domains": domains,
            "uuid4s": uuid4s,
        }
        ie = IndraEvent()
        ie.domain = "$trx/db/req/del"
        ie.from_id = "ws/python"
        ie.data_type = "json/reqdel"
        if self.session_id is not None:
            ie.auth_hash = self.session_id
        ie.data = json.dumps(cmd)
        return await self.send_event(ie)

    async def delete_recs_wait(self, domains: str | list[str] | None = None, uuid4s: str | list[str] | None = None):
        future = await self.delete_recs(domains, uuid4s)
        if future is None:
            return None
        result = await future
        if result.data_type.startswith("error") is True:
            self.log.error(f"Error: {result.data}")
            return None
        else:
            try:
                res:int = cast(int, json.loads(result.data))  # Number of deleted records
            except Exception as e:
                self.log.error(f"Failed to parse delete_recs cnt: {e}")
                return None
            return res

    async def update_recs(self, recs: IndraEvent | list[IndraEvent]):
        if isinstance(recs, list) is False:
            self.log.error("Not a list")
            recsl: list[IndraEvent] = [cast(IndraEvent, recs)]
        else:
            recsl = cast(list[IndraEvent], recs)
        cmd = recsl
        ie = IndraEvent()
        ie.domain = "$trx/db/req/update"
        ie.from_id = "ws/python"
        ie.data_type = "json/requpdate"
        if self.session_id is not None:
            ie.auth_hash = self.session_id
        ie.data = json.dumps(cmd)
        return  await self.send_event(ie)

    async def update_recs_wait(self, recs: IndraEvent | list[IndraEvent]):
        future = await self.update_recs(recs)
        if future is None:
            return None
        result = await future
        if result.data_type.startswith("error") is True:
            self.log.error(f"Error: {result.data}")
            return None
        else:
            num_updated:int = cast(int, json.loads(result.data))
        return num_updated

    async def kv_write(self, key:str, value:str):
        cmd: dict[str, str] = {
            "key": key,
            "value": value,
        }
        ie = IndraEvent()
        ie.domain = "$trx/kv/req/write"
        ie.from_id = "ws/python"
        ie.data_type = "kvwrite"
        if self.session_id is not None:
            ie.auth_hash = self.session_id
        ie.data = json.dumps(cmd)
        return await self.send_event(ie)

    async def kv_write_wait(self, key:str, value:str):
        future = await self.kv_write(key, value)
        if future is None:
            return None
        result = await future
        if result.data_type.startswith("error") is True:
            self.log.error(f"Error: {result.data}")
            return None
        else:
            try:
                status: str =  cast(str, json.loads(result.data))  # "OK"
            except Exception as e:
                self.log.error(f"Failed to parse state {e}")
                return None
            return status

    async def kv_read(self, key:str):
        cmd = {
            "key": key,
        }
        ie = IndraEvent()
        ie.domain = "$trx/kv/req/read"
        ie.from_id = "ws/python"
        ie.data_type = "kvread"
        if self.session_id is not None:
            ie.auth_hash = self.session_id
        ie.data = json.dumps(cmd)
        self.log.debug("Sending kv_read")
        return await self.send_event(ie)

    async def kv_read_wait(self, key:str) -> str | None:
        future = await self.kv_read(key)
        if future is None:
            return None
        result = await future
        if result.data_type.startswith("error") is True:
            self.log.error(f"Error: {result.data}")
            return None
        else:
            try:
                value: str = cast(str, json.loads(result.data))
            except Exception as e:
                self.log.error(f"Failed to parse result {e}")
                return None
            return value

    async def kv_delete(self, key:str):
        cmd = {
            "key": key,
        }
        ie = IndraEvent()
        ie.domain = "$trx/kv/req/delete"
        ie.from_id = "ws/python"
        ie.data_type = "kvdelete"
        if self.session_id is not None:
            ie.auth_hash = self.session_id
        ie.data = json.dumps(cmd)
        return await self.send_event(ie)

    async def kv_delete_wait(self, key: str) -> str | None:
        future = await self.kv_delete(key)
        if future is None:
            return None
        result = await future
        if result.data_type.startswith("error") is True:
            self.log.error(f"Error: {result.data}")
            return None
        else:
            try:
                status: str = cast(str, json.loads(result.data))
            except Exception as e:
                self.log.error(f"Failed to parse result {e}")
                return None
            return status

    async def login(self, username:str, password:str):
        cmd = {
            "key": f"entity/indrajala/user/{username}/password",
            "value": password,
        }
        self.username = username
        ie = IndraEvent()
        ie.domain = "$trx/kv/req/login"
        ie.from_id = "ws/python"
        ie.data_type = "kvverify"
        if self.session_id is not None:
            ie.auth_hash = self.session_id
        ie.data = json.dumps(cmd)
        return await self.send_event(ie)

    async def login_wait(self, username:str, password:str):
        # Login and return the auth_hash session_id.
        #
        #  @param username: username
        #  @param password: password
        #  @return: auth_hash or None
        #
        #  WARNING: this function is SLOW, since login uses salted hashes on server-side
        #  which require about 200ms to compute
        #  so expect a delay of about 200ms + transport time (about 50ms min.)
        future = await self.login(username, password)
        if future is None:
            return None
        result = await future
        if result.data_type.startswith("error") is True:
            self.log.error(f"Error: {result.data}")
            self.session_id = None
            self.username = None
            return None
        else:
            self.log.debug(
                f"Login result: {result.data}, {result.data_type}, {result.auth_hash}"
            )
            self.session_id = result.auth_hash
            return result.auth_hash

    async def logout(self):
        ie = IndraEvent()
        ie.domain = "$trx/kv/req/logout"
        ie.from_id = "ws/python"
        if self.session_id is not None:
            ie.auth_hash = self.session_id
        ie.data_type = ""
        ie.data = ""
        return await self.send_event(ie)

    async def logout_wait(self):
        future = await self.logout()
        if future is None:
            return False
        result = await future
        if result.data_type.startswith("error") is True:
            self.log.error(f"Error: {result.data}")
            return False
        else:
            return True

    async def indra_log(self, level:str , message:str , module_name:str | None=None):
        """Log message"""
        if module_name is None:
            module_name = self.module_name
        if level not in ["debug", "info", "warn", "error"]:
            self.log.error(f"Invalid log level: {level}, {message}")
            return False
        ie = IndraEvent()
        ie.domain = f"$log/{level}"
        ie.from_id = f"ws/python/{module_name}"
        ie.data_type = "log"
        if self.session_id is not None:
            ie.auth_hash = self.session_id
        ie.data = json.dumps(message)
        return await self.send_event(ie)

    async def debug(self, message: str, module_name:str | None=None):
        self.log.debug(f"Indra_log-Debug: {message}")
        return await self.indra_log("debug", message, module_name)

    async def info(self, message:str, module_name:str | None=None):
        self.log.info(f"Indra_log-Info: {message}")
        return await self.indra_log("info", message, module_name)

    async def warn(self, message:str, module_name:str | None=None):
        self.log.warning(f"Indra_log-Warn: {message}")
        return await self.indra_log("warn", message, module_name)

    async def error(self, message:str, module_name:str | None=None):
        self.log.error(f"Indra_log-Error: {message}")
        return await self.indra_log("error", message, module_name)

    @staticmethod
    def get_timeseries(result: list[tuple[float, float]]):
        dt: list[datetime.datetime] = []
        y: list[float]= []
        for t, yv in result:
            dt.append(IndraTime.julian_to_datetime(t))
            y.append(yv)
        return dt, y
