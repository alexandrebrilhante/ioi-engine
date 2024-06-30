import socket
from os import environ
from typing import Callable, Dict, Optional
from uuid import uuid1

import simplefix
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

FIX_TAGS: Dict[str, int] = {
    "ioi_id": 23,
    "ioi_trans_type": 28,
    "ioi_ref_id": 26,
    "symbol": 55,
    "no_underlyings": 711,
    "side": 54,
    "qty_type": 854,
    "ioi_qty": 27,
    "currency": 15,
    "no_legs": 555,
    "price_type": 423,
    "price": 44,
    "valid_until_time": 62,
    "ioi_qlty_ind": 25,
    "ioi_natural_flag": 130,
    "no_ioi_qualifiers": 199,
    "text": 58,
    "encoded_text_len": 354,
    "encoded_text": 355,
    "transact_time": 60,
    "url_link": 149,
    "no_routing_ids": 215,
    "routing_type": 216,
    "routing_id": 217,
    "checksum": 10,
}


class IOI(BaseModel):
    ioi_id: str
    ioi_trans_type: str
    ioi_ref_id: str | None
    symbol: str
    no_underlyings: str | None
    side: str
    qty_type: str | None
    ioi_qty: str
    currency: str | None
    no_legs: str | None
    price_type: str | None
    price: str | None
    valid_until_time: str | None
    ioi_qlty_ind: str | None
    ioi_natural_flag: str | None
    no_ioi_qualifiers: str | None
    text: str | None
    encoded_text_len: str | None
    encoded_text: str | None
    transact_time: str | None
    url_link: str | None
    no_routing_ids: str | None
    routing_type: str | None
    routing_id: str | None
    checksum: str


class IndicationOfInterest:
    def __init__(self, **kwargs) -> None:
        self.message = simplefix.FixMessage()

        self.set_headers()

        for key, value in kwargs.items():
            if key in self.FIX_TAGS:
                self.message.append_pair(FIX_TAGS[key], value)

        if "checksum" not in kwargs:
            self.message.append_pair(10, environ["CHECKSUM"])

    def _set_headers(self) -> None:
        self.message.append_pair(8, "FIX.4.4", header=True)
        self.message.append_pair(35, 6, header=True)
        self.message.append_pair(49, environ["SENDER"], header=True)
        self.message.append_pair(56, environ["TARGET"], header=True)
        self.message.append_pair(34, 4684, header=True)
        self.message.append_time(52, header=True)

    def _send(self) -> bytes:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((environ["HOST"], environ["PORT"]))
            s.sendall(self.message.encode())

    def submit(self) -> Callable:
        assert (
            self.message["symbol"] is not None
            and self.message["side"] is not None
            and self.message["ioi_qty"] is not None
        ), "Symbol, side, and IOI quantity are required..."

        self.message.append_pair(26, str(uuid1()))
        self.message.append_pair(28, "N")

        return self._send()

    def replace(self) -> Callable:
        assert self.message["ioi_ref_id"] is not None, "IOI ref ID required..."

        self.message.append_pair(26, self.message["ioi_ref_id"])
        self.message.append_pair(28, "R")

        return self._send()

    def cancel(self) -> Callable:
        assert self.message["ioi_ref_id"] is not None, "IOI ref ID required..."

        self.message.append_pair(26, self.message["ioi_ref_id"])
        self.message.append_pair(28, "C")

        return self._send()


@app.get("/api/v1/ioi/submit")
def submit(tags: Dict[str, Optional[int | str]]):
    ioi = IndicationOfInterest(tags)
    ioi.submit()

    return {"status": "submitted"}


@app.get("/api/v1/ioi/replace")
def replace(tags: Dict[str, Optional[int | str]]):
    ioi = IndicationOfInterest(tags)
    ioi.replace()

    return {"status": "replaced"}


@app.get("/api/v1/ioi/cancel")
def cancel(tags: Dict[str, Optional[int | str]]):
    ioi = IndicationOfInterest(tags)
    ioi.cancel()

    return {"status": "cancelled"}
