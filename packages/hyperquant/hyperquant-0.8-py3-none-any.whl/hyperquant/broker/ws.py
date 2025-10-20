import asyncio
import base64
import time
from typing import Any

import pybotters
from pybotters.ws import ClientWebSocketResponse, logger
from pybotters.auth import Hosts
import urllib
import yarl


class Heartbeat:
    @staticmethod
    async def ourbit(ws: pybotters.ws.ClientWebSocketResponse):
        while not ws.closed:
            await ws.send_str('{"method":"ping"}')
            await asyncio.sleep(10.0)
    
    async def ourbit_spot(ws: pybotters.ws.ClientWebSocketResponse):
        while not ws.closed:
            await ws.send_str('{"method":"ping"}')
            await asyncio.sleep(10.0)

    @staticmethod
    async def edgex(ws: pybotters.ws.ClientWebSocketResponse):
        while not ws.closed:
            now = str(int(time.time() * 1000))
            await ws.send_json({"type": "ping", "time": now})
            await asyncio.sleep(20.0)

    @staticmethod
    async def lbank(ws: ClientWebSocketResponse):
        while not ws.closed:
            await ws.send_str('ping')
            await asyncio.sleep(6)

pybotters.ws.HeartbeatHosts.items['futures.ourbit.com'] = Heartbeat.ourbit
pybotters.ws.HeartbeatHosts.items['www.ourbit.com'] = Heartbeat.ourbit_spot
pybotters.ws.HeartbeatHosts.items['quote.edgex.exchange'] = Heartbeat.edgex
pybotters.ws.HeartbeatHosts.items['uuws.rerrkvifj.com'] = Heartbeat.lbank

class WssAuth:
    @staticmethod
    async def ourbit(ws: ClientWebSocketResponse):
        key: str = ws._response._session.__dict__["_apis"][
            pybotters.ws.AuthHosts.items[ws._response.url.host].name
        ][0]
        await ws.send_json(
            {
                "method": "login",
                "param": {
                    "token": key
                }
            }
        )
        async for msg in ws:
            # {"channel":"rs.login","data":"success","ts":1756470267848}
            data = msg.json()
            if data.get("channel") == "rs.login":
                if data.get("data") == "success":
                    break
                else:
                    logger.warning(f"WebSocket login failed: {data}")
    
pybotters.ws.AuthHosts.items['futures.ourbit.com'] = pybotters.auth.Item("ourbit", WssAuth.ourbit)
